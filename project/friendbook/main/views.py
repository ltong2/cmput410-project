from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from django.db import IntegrityError
from main.models import Users, Posts, Comment
import json
import time
from datetime import datetime
import urllib2

@require_http_methods(["GET", "POST"])
def index(request):
    context = RequestContext(request)

    if (request.method == "GET"):
        return render_to_response('main/index.html', context)
    else:
        if ("login" in request.POST):
            username = request.POST["username"]
            password = request.POST["password"]
            
            if (len(Users.objects.filter(username = username, password = password)) == 1):
                request.session["loggedIn"] = True
                request.session["username"] = username
                
                return redirect("wall")
            else:
                return render_to_response("main/index.html", {"loginError": "Error: wrong username/password"}, context)
        else:
            username = request.POST["username"]
            password = request.POST["password"]
            role = "Author"
            registerDate = datetime.now().date()
            active = 0
            github = request.POST["github"]
            
            if ((username == "") or (password == "")):
                return render_to_response('main/index.html', {"signupError": "Error: one or more missing fields"}, context)
            
            try:
                newUser = Users(username=username, password=password, role=role, register_date=registerDate, active=active, github_account=github)
                newUser.save()
            except IntegrityError as e:
                return render_to_response('main/index.html', {"signupError": "Error: username already exists"}, context)
            
            return render_to_response('main/index.html', {"signupSuccess": "Successfully created an account! Before you can login, the website admin has to verify who you are"}, context)


@require_http_methods(["GET"])
def logout(request):
  context = RequestContext(request)

  request.session["loggedIn"] = False
  request.session["username"] = ""

  return redirect("index")
  
def server_admin(request):
  if request.method == 'GET':
    context = RequestContext(request)
    context['users'] = list(Users.objects.all())
    return render_to_response('main/server_admin.html', context)

def users(request):
  if request.method == 'GET':
    response_data = serializers.serialize('json', Users.objects.all())
    return HttpResponse(response_data)
  else:
    return HttpResponseNotAllowed

def getGitHubEvents(userName):
    response = urllib2.urlopen("https://api.github.com/users/"+userName+"/events").read()
    eventList = json.loads(response)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def wall(request):
    context = RequestContext(request)
    if request.method == "POST":
        title = request.POST["post_title"]
        author_id = Users.objects.get(username=request.session["username"])

        permission = request.POST["post_permissions"]
        source = request.POST["post_source"]
        origin = request.POST["post_origin"]
        category = request.POST["post_category"]
        description = request.POST["post_description"]
        content_type = "text/html"
        content = request.POST["post_content"]
        pub_date = datetime.now().date()

        post = Posts(title = title, source=source, origin=origin, category=category, description=description, content_type=content_type, content=content, owner_id=author_id, permission=permission, pub_date=pub_date, visibility = permission)
        post.save()
        return redirect("wall")
    else:
        return render_to_response('main/postwall.html', context)

def newpost(request):
    print "got new post"
    context = RequestContext(request)
    return render_to_response('main/create_post.html', context)


'''
    RESTful API for One author's posts
    
    This function is called when /author/<user_id>/posts is called with GET, POST,
    PUT or DELETE HTTP requests and it shows information about author's
    posts.
    
    For GET requests, it returns all posts that the user has access to.
    For POST requests, if an id is specified and if the post exists, then it
    will update the post to newly given information in POST request body if 
    the specified user is the author.  If the post does not exist in the
    database, then it will create a new post with specified author as an author.
    For PUT request, it will create the posts in the PUT request body.
    For DELETE request, it will delete all posts that the specified user has
    authored.
'''
@csrf_exempt
def posts(request, user_id):#todo get rid of username (currently it throws an error)
    context = RequestContext(request)
    print request.method
    if request.method == 'GET':
        print "restful get requested"
        getGitHubEvents(request.session["username"])
        # TODO: change this!! hard coded username for now for testing
        userInfo = Users.objects.get(username=request.session["username"])
        posts = Posts.objects.filter(owner_id=userInfo).order_by("-pub_date")
        currentHost = request.get_host()
        jsonResult = post2Json(currentHost, userInfo, posts)
        # must have content_type parameter to not include HTTPResponse
        # values included in the JSON result to be passed to the AJAX call
        return HttpResponse(jsonResult, content_type="application/json")
    
    elif request.method == 'POST':
        print "restful POST requested"
    elif request.method == 'PUT':
        print "restful PUT requested"
        #create post in db
    elif request.method == 'DELETE':
        #delete post in db
        print "restful DELETE requested"
    else:
        return HttpResponseNotAllowed

'''
This method is called by posts to format the query result as desired JSON format
as ones shown in example_article.json in project webisite:
https://github.com/abramhindle/CMPUT404-project-socialdistribution/blob/master/example-article.json

It takes the database query result and pases the QuerySet and create a properly formatted JSON object.

@param querySet         django QuerySet object that is returned from database query to 
                        posts table
@return JSON object to be sent as a response to an AJAX call
    
'''
def post2Json(host, userData, queryset):
    # TODO Date format is currently wrong! May have to change
    # the format when it's being inserted into DB
    querylist = []
    for queryResult in queryset:
        user = {}
        user["id"] = userData.id
        # TODO change this when we are communicating with other servers
        # they may have to specify their url?
        user["host"] = host
        user["displayname"] = userData.username
        user["url"] = host+"/author/"+str(userData.id)
        
        post = {}
        post["title"] = queryResult.title
        post["source"] = queryResult.source
        post["origin"] = queryResult.origin
        post["description"] = queryResult.description
        post["content_type"] = queryResult.content_type
        post["content"] = queryResult.content
        post["author"] = user
        categories = queryResult.category.split(",")
        post["categories"] = categories
        comments = {}
        commentObject = Comment.objects.filter(post_id=queryResult.id)
        for commentResult in commentObject:
            commentAuthor = {}
            CommentAuthorInfo = Users.objects.get(id=commentResult.owner_id)
            commentAuthor["id"] = CommentAuthorInfo.id
            commentAuthor["host"] = host
            commentAuthor["displayname"] = CommentAuthorInfo.username
            comments["author"] = commentAuthor
            comments["comment"] = commentResult.comment
            comments["pubDate"] = commentResult.pub_date
            #should be SHA1 or UUID encrypted?
            comments["guid"] = commentResult.id
        post["comments"] = comments
        post["pubDate"] = queryResult.pub_date
        #should be SHA1 or UUID encrypted?
        post["guid"] = queryResult.id
        post["visibility"] = queryResult.visibility
        querylist.append(post)
    return json.dumps(querylist, default=date_handler)

'''
date_handler function changes the date format to the one
that can be serialized by the json python library

@param obj      datetime object to be handled
@return         date format that can be serialized by the json library

'''
# code taken from:
# http://blog.codevariety.com/2012/01/06/python-serializing-dates-datetime-datetime-into-json/
def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

'''
This method get the current host URL to be inserted into the database.
The URL is in form of http://IP address or domain name:port
'''
# code from http://fragmentsofcode.wordpress.com/2009/02/24/django-fully-qualified-url/
def current_site_url():
    """Returns fully qualified URL (no trailing slash) for the current site."""
    from django.contrib.sites.models import Site
    current_site = Site.objects.get_current()
    protocol = getattr(settings, 'MY_SITE_PROTOCOL', 'http')
    port     = getattr(settings, 'MY_SITE_PORT', '')
    url = '%s://%s' % (protocol, current_site.domain)
    if port:
        url += ':%s' % port
    return url

'''
    RESTful API for getting information on one post specified in post_id
    of the URI
    
    This function is called when /author/<user_id>/posts/<post_id> is called with GET, POST,
    PUT or DELETE HTTP requests and it shows information about the specified post.
    
    For GET requests, it returns relevant information about the specified post.(the
    user must have access to this post!)
    For POST requests, if an id is specified and if the post exists, then it
    will update the post to newly given information in POST request body if
    the specified user is the author.  If the post does not exist in the
    database, then it will create a new post with specified author as an author.
    For PUT request, it will create a post in the PUT request body.
    For DELETE request, it will delete all post if the user specified is an author of
    the post.
    
'''
@csrf_exempt
def post (request, user_id, post_id):
  print request.method
  if request.method == 'GET':
    reponse_data = serializers.serialize('json', Posts.objects.filter(owner_id=Users.objects.get(username=username)),use_natural_foreign_keys=True)
    return HttpResponse(reponse_data)
  elif request.method == 'POST':
    #modify post
    doSOmething()
  elif request.method == 'DELETE':
    #delete post
    #eg curl -X DELETE http://localhost:8000/friendbook/user/jasonreddekopp/post/1/
    Posts.objects.get(id=post_id).delete()
    return HttpResponse("Post Deleted\n")
  else: 
    return HttpResponseNotAllowed

def images (request, username):
  if request.method == 'GET':
    return HttpResponse("all images from " + username)
  else: 
    return HttpResponseNotAllowed

def image (request,username,image_id):
  if request.method == 'GET':
    return HttpResponse("image: " + image_id + ", from " + username)
  elif request.method == 'POST':
    #modify image
    doSomething()
  elif request.method == 'PUT':
    #add image
    doSomething()
  elif request.method == 'DELETE':
    #delete image
    doSomething()
  else: 
    return HttpResponseNotAllowed
  
def friends (request,username):
  return HttpResponse("all friends of " + username)


def friend (request, username, friend_id):
  if request.method == 'GET':
    return HttpResponse("friend : " + friend_id + ", from " + username)
  elif request.method == 'POST':
    #modify friend
    doSomething()
  elif request.method == 'PUT':
    #add friend
    doSomething()
  elif request.method == 'DELETE':
    #delete friend
    doSomething()
  else: 
    return HttpResponseNotAllowed
  
@csrf_exempt
def user(request, username):
  context=RequestContext(request)
  if request.method == 'GET':
    user = Users.objects.get(username=username)
    reponse_data = serializers.serialize('json', [user])
    return HttpResponse(reponse_data) 
  elif request.method == 'POST':
    user = Users.objects.get(username=request.POST['username'])
    if   (request.POST['method']=="delete"):
      Users.objects.get(username=request.POST['username']).delete()
      context['users'] = list(Users.objects.all())
      return render_to_response('main/server_admin.html', context)
    elif (request.POST['method']=="change"):
      context['userprofile']= [user]
      context['users'] = list(Users.objects.all())
      return render_to_response('main/auth_user.html', context)
    elif (request.POST['method']=="add"):
      user.active = True
      user.save()
      context['users'] = list(Users.objects.all())
      return render_to_response('main/server_admin.html', context)
    elif (request.POST['method']=="edit"):
      if 'name' in request.POST:
        doSomething()
      elif 'password' in request.POST:
        user.password = request.POST['password']
      elif 'role' in request.POST:
        user.role = request.POST['role']
      elif 'register_date' in request.POST:
        user.register_date = request.POST['register_date']
      elif 'github_account' in request.POST:
        user.github_account = request.POST['github_account']
      user.save()
      context['users'] = list(Users.objects.all())
      return render_to_response('main/server_admin.html', context)
    else:
      return HttpResponse("Error")

  elif request.method == 'PUT':
    #add user 
    #eg curl -X PUT -H "Content-Type: application/json" -d '{"password":"asdf", "role":"author"}' http://localhost:8000/friendbook/user/jasonreddekopp/
    if(Users.objects.filter(username=username).count() > 0 ):
      return HttpResponse("User exists\n")
    b = json.loads(request.body)
    Users.objects.create(username = username, password = b['password'], role = b['role'], active = False, github_account = "")
    return HttpResponse("User Created\n")
  elif request.method == 'DELETE':
    #delete user
    #eg curl -X DELETE http://localhost:8000/friendbook/user/jasonreddekopp/
    Users.objects.get(username=username).delete()
    return HttpResponse("User Deleted\n")
  else: 
    return HttpResponseNotAllowed

def doSomething():
  return null


