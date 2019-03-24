from django.shortcuts import render, redirect, get_object_or_404
from .models import Article, Tag, User, Comment, RateComment, ColorScheme, Layout, Request
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import views as auth_views
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_out
from django.http import HttpResponseRedirect
from django.db.models import Count, Min, Max, Avg, Q

def registered_required(user):
    return user.is_authenticated

def editor_required(user):
        if user.is_authenticated:
            return user.is_editor()
        return False


def author_required(user):
        if user.is_authenticated:
            return user.is_author()
        return False


def editor_or_author_required(user):
    if user.is_authenticated:
        return user.is_editor() or user.is_author()
    return False

def executive_editor_required(user):
    if user.is_authenticated:
        return user.is_executive_editor()
    return False

def admin_required(user):
    if user.is_authenticated:
        return user.is_admin()

def index(request):
    article = Article.objects.filter(is_published=True)
    colors = ColorScheme.objects.all()
    try:
        layout = Layout.objects.get()
        layout_first = False
    except Layout.DoesNotExist:
        layout = 'layout_one_column.html'
        layout_first = True
    u = request.user
    if request.method == 'POST':

        if 'color' in request.POST and u.is_admin():
            color_form = ColorForm(request.POST)
            if color_form.is_valid():
                # if-checken nedenfor vil for en eller annen grunn aldri naa else
                if color_form.cleaned_data['color'].casefold() not in colors:
                    colors.delete()
                    color_form.save()
                    print("VALUE: " + str(colors))
                    print("FORM " + str(color_form.cleaned_data['color']))
                    messages.success(request, 'Color updated!')
                else:
                    messages.success(request, 'Color already on site!')

        else:
            layout_form = LayoutForm(request.POST)
            print(layout_form.is_valid())
            if layout_form.is_valid():
                if not layout_first:
                    layout.delete()
                layout_form.save()
                messages.success(request, 'Layout updated!')
        return redirect('index')
    else:
        color_form = ColorForm()
        layout_form = LayoutForm()
    print(article)
    print(request)
    context = {
        'articles': article,
        'color_form': color_form,
        'color': colors,
        'layout_form' : layout_form,
        'layout' : layout,
    }
    return render(request, 'index.html', context=context)


@user_passes_test(registered_required, '/login/')
def favorite(request):
    favourite_articles = ''
    if request.user.is_authenticated:
        favourite_articles = request.user.favorites.all()
    context = {
        'articles': favourite_articles,
    }

    return render(request, 'favourite_list.html', context=context)


def index_tag(request, tag):
    article = Article.objects.filter(tag__name=tag, is_published=True)
    index_tag = True
    try:
        layout = Layout.objects.get()
    except Layout.DoesNotExist:
        layout = 'layout_one_column.html'
    if not article:
        messages.warning(request, 'There are no articles with this tag.')

    context = {
        'articles': article,
        'layout': layout,
        'index_tag':index_tag,
    }

    return render(request, 'index.html', context=context)


@user_passes_test(editor_or_author_required, '/login/')
def editor(request):
    if editor_required(request.user):
        article = Article.objects.all()
        context = {
            'articles': article
        }
    else:
        article = Article.objects.filter(author=request.user)
        context = {
            'articles': article
        }
    return render(request, 'editor.html', context=context)


def login(request):
    return render(request, 'login.html')


def user(request):
    return render(request, 'user.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account successfully created! You can now log in.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})



def search(request):
    query = request.GET['q']

    filter_title = Article.objects.filter(title__icontains=query)
    filter_text = Article.objects.filter(text__icontains=query)
    try:
        layout = Layout.objects.get()
    except Layout.DoesNotExist:
        layout = 'layout_one_column.html'

    articles = filter_title | filter_text

    context = {
        'articles': articles,
        'layout': layout,
        'search_tag': True,
    }

    return render(request, 'index.html', context=context)


def post_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    comments = article.comments.filter(active=True)
    ratecomments = article.ratecomments.filter(active=True)
    comment_form = ""
    ratecomment_form = ""
    u = request.user
    if request.method == 'GET':
        if 'favorite' in request.GET and u.is_authenticated:
            print(request.POST)
            u.favorites.add(article)
            u.save()
            messages.success(request, 'Article added to favorites!')
        if 'delete' in request.GET and u.is_authenticated:
            u.favorites.remove(article)
            u.save()
            messages.success(request, 'Article removed from favorites!')

    if request.method == 'POST':
        if request.method == 'POST' and not article.is_published:
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.post = article
                new_comment.save()
                messages.success(request, 'Your comment has been successfully added to the article')
    else:
        if request.user.is_authenticated:
            comment_form = CommentForm(initial={'name': request.user.name, 'email': request.user.email})
    if request.method == 'POST' and article.is_published == True:
        ratecomment_form = RateCommentForm(data=request.POST)
        if ratecomment_form.is_valid():
            new_ratecomment = ratecomment_form.save(commit=False)
            new_ratecomment.post = article
            new_ratecomment.save()
            messages.success(request, 'Your comment has been successfully added to the article')
    else:
        if request.user.is_authenticated:
            ratecomment_form = RateCommentForm(initial={'name': request.user.name, 'email': request.user.email})
    context = {
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
        'ratecomment_form': ratecomment_form,
        'ratecomments': ratecomments,
    }
    return render(request, 'post_detail.html', context=context)


@user_passes_test(author_required, '/login/')
def post_new(request):
    if request.method == "POST":
        form = PostFormNew(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=True)
            article.save()
            return redirect('post_detail', pk=article.pk)
    else:
        form = PostFormNew(initial={'author': request.user})
    return render(request, 'post.html', {'form': form})


@user_passes_test(editor_or_author_required, '/login/')
def post_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.user not in article.assigned_proof_read.all() and not request.user.is_executive_editor() and not request.user in article.author.all():
        messages.warning(request, 'You do not have editor permission to this article')
        return redirect('login')

    if (not request.user.is_editor()) and (request.user not in article.author.all()): #LOL
        return redirect('/login/')
    else:
        if request.method == "POST":
            form = PostFormEdit(request=request, data=request.POST,files=request.FILES, instance=article)
            if form.is_valid() and 'submit' in request.POST:
                article = form.save(commit=True)
                article.save()
                return redirect('post_detail', pk=article.pk)
            elif 'delete' in request.POST: #strengt tatt ikke noedvendig aa sjekke igjen
                article.delete()
                messages.success(request, 'Your article "' + str(article) + ' was "deleted')
                return redirect('editor')
        else:
            form = PostFormEdit(request=request, instance=article)
        return render(request, 'post.html', {'form': form, 'article': article})


def browse_tags(request):
    num_tags = Tag.objects.all().count()
    tags = Tag.objects.all()

    if request.method == "POST":
        form = CreateTagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=True)
            tag.save()
    else:
        form = CreateTagForm()

    context = {
        'num_tags': num_tags,
        'tags': tags,
        'form': form,
    }

    return render(request, 'browse_tags.html', context=context)



@user_passes_test(registered_required, '/login/')
def feed(request):
    tags = Tag.objects.all()
    article = (Article.objects.filter(author__in=request.user.subscribe_author.all()) | Article.objects.filter(tag__in=request.user.subscribe_tag.all())).distinct()
    context = {
        'articles': article,
        'tags': tags,
    }

    return render(request, 'feed.html', context=context)


@user_passes_test(registered_required, '/login/')
def feed_tag(request, tag):
    x = Tag.objects.get(name=tag)
    if x in request.user.subscribe_tag.all():
        request.user.subscribe_tag.remove(x)
        request.user.save()
    else:
        request.user.subscribe_tag.add(x)
        request.user.save()
    tags = Tag.objects.all()
    article = (Article.objects.filter(author__in=request.user.subscribe_author.all()) | Article.objects.filter(tag__in=request.user.subscribe_tag.all())).distinct()
    context = {
        'articles': article,
        'tags': tags,
    }

    return render(request, 'feed.html', context=context)


def profile(request, id=id):
    u = User.objects.get(id=id)
    users_articles = Article.objects.filter(author=u)
    #Requests = u.requests.filter(active=True)
    request_form = ""

    if request.method == 'POST':
        request_form = RequestForm(data=request.POST)

        if request_form.is_valid():
            new_request = request_form.save(commit=False)
            new_request.user = request.user
            new_request.save()
            messages.success(request, 'Request for new role sent')
    else:
        if request.user.is_authenticated:
            request_form = RequestForm()

    context = {
        'u': u,
        'users_articles': users_articles,
        #'request': Requests,
        'request_form': request_form,
    }

    if request.method == "POST":
        if 'subscribe' in request.POST:
            request.user.subscribe_author.add(u)
            request.user.save()
        if 'unsubscribe' in request.POST:
            request.user.subscribe_author.remove(u)
            request.user.save()

    return render(request, 'profile.html', context=context)


def profile_edit(request, id):
    u = User.objects.get(id=id)
    if u == request.user or request.user.is_superuser:
        if request.method == "POST":
            form = EditUserForm(data=request.POST, files=request.FILES, instance=u)
            if form.is_valid():
                form.save()
                return redirect('profile', id=u.id)
        else:
            form = EditUserForm(instance=u)

        context = {
            'form': form
        }
        return render(request, 'edit_profile.html', context=context)
    else:
        messages.info(request, 'You do not have permission to view this page')
        return redirect(request, '/login/')


@receiver(user_logged_out)
def on_user_logged_out(request, **kwargs):
    messages.info(request, 'You have been logged out.')


@user_passes_test(executive_editor_required, '/login/')
def analyze(request):
    users = User.objects.annotate(
        num_articles=Count('author',  distinct=True),
        num_following=Count('subscribe_author', distinct=True),
        num_tag=Count('subscribe_tag', distinct=True),
    )
    articles = Article.objects.annotate(
        avg_rating=Avg('ratecomments__rating', distinct=True),
        num_comments=Count('ratecomments', distinct=True),
        num_favorites=Count('favorites', distinct=True),
    )
    tags = Tag.objects.annotate(
        num_subs=Count('subscribe_tag', distinct=True),
        num_articles=Count('article_tag', filter=Q(article_tag__is_published=True),distinct=True),
    )

    num_articles = Article.objects.all().count()

    num_tags = Tag.objects.count()
    if num_articles>0:
        avg_rating_all = Article.objects.aggregate(Avg('ratecomments__rating'))

    avg_comments_all = Article.objects.aggregate(Count('ratecomments'))
    avg_favorites_all = Article.objects.aggregate(Count('favorites'))
    avg_tag_all = Tag.objects.aggregate(Count('subscribe_tag'))

    avg_tag_all = max(1,(avg_tag_all.get('subscribe_tag__count')))
    avg_comments_all = max(1, (avg_comments_all.get('ratecomments__count')))
    avg_favorites_all = max(1, (avg_favorites_all.get('favorites__count')))

    avg_tag_all = avg_tag_all/num_tags
    avg_comments_all = avg_comments_all/num_articles
    avg_favorites_all = avg_favorites_all/num_articles

    context = {
        'users': users,
        'articles': articles,
        'tags': tags,
        'avg_rating_all':avg_rating_all,
        'avg_comments_all':avg_comments_all,
        'avg_favorites_all':avg_favorites_all,
        'avg_tag_all':avg_tag_all,
    }
    return render(request, 'analyze.html', context=context)
