/**
 * Javascript used in postwall.html
 */
$(document).ready(function (){
    $("#spec_author_div").hide();
    $(".post-overlays").css("display", "none");
    $("#post_permissions").change(function() {
        var currentVal = $(this).val();
        if(currentVal == "spec_autor")
        {
            $("#spec_author_div").show();
        }
        else
        {
            $("#spec_author_div").hide();
        }
    });
    
    $(".blog-post").mouseover(function() {
        var currentdivId = $(this).attr('id').split("-");
        var overlayheight = $(this).height();
        
        var currentTop = $(this).position().top;
         
        $("#post_overlay-"+currentdivId[1]).css("top", currentTop);

        $("#post_overlay-"+currentdivId[1]).css("display", "block");

        $("#post_overlay-"+currentdivId[1]).stop(true, true).animate({
            height: overlayheight+50
        }, 1000); 
    });
    
    $(".blog-post").mouseleave(function() {
        var currentdivId = $(this).attr('id').split("-");
        $("#post_overlay-"+currentdivId[1]).stop(true, true).animate({
            height: "30px"
        }, 300);
        $("#post_overlay-"+currentdivId[1]).css("display", "none");
    });
    
    $(".overlayEdit").click(function() {
        // reactivate the tinymce with the contents inside
        var currentdbId = $(this).attr("id").split("-")[1];
        
        text2form(currentdbId);
        
        $("#edit_cancel").click(function(e) {
            e.preventDefault();
            $("#post_overlay-"+currentdbId).css("display", "block");
            $("#post-"+currentdbId).css("display", "block");
            $("#edit_post-"+currentdbId).empty().remove();
            
            // rebind mouse listener
            $(".blog-post").mouseover(function() {
                var currentdivId = $(this).attr('id').split("-");
                var overlayheight = $(this).height();
                
                var currentTop = $(this).position().top;
                 
                $("#post_overlay-"+currentdivId[1]).css("top", currentTop);
        
                $("#post_overlay-"+currentdivId[1]).css("display", "block");
        
                $("#post_overlay-"+currentdivId[1]).stop(true, true).animate({
                    height: overlayheight+50
                }, 1000); 
            });
            
            $(".blog-post").mouseleave(function() {
                var currentdivId = $(this).attr('id').split("-");
                $("#post_overlay-"+currentdivId[1]).stop(true, true).animate({
                    height: "30px"
                }, 300);
                $("#post_overlay-"+currentdivId[1]).css("display", "none");
            });
        });
        
    });
    
    tinymce.init({
        selector: "textarea",
        plugins: [
            "advlist autolink lists link image charmap preview anchor",
            "searchreplace visualblocks code fullscreen",
            "insertdatetime media table contextmenu paste"
        ],
        toolbar: "insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image"
    });
    
    $("#new_post").submit(function(e) {
        e.preventDefault();
        processPostData();
    });

});
//
//function processPostData()
//{
//    var permission = $("#post_permissions").val();
//    var authorname = $("#spec_author_input").val();
//    var title = $("#post_title").val();
//    var description = $("#post_description").val();
//    var content = tinymce.get("post_content").getContent();
//    var host = window.location.host;
//    var posttime = $.now();
//    
//    var source = $("#post_source").val()
//    //var origin = not done yet
//    //var category = not implemented yet
//    //var guid = ??
//    
//    // make the JSON string and pass to AJAX and call url
//    // not tested yet!
//    var targetUrl = $("#new_post").attr("action");
//    $.ajax({
//        url: targetUrl,
//        type: 'PUT',
//        contentType: 'text/html',
//        data:{
//            "posts":[
//                {
//                    "title": title,
//                    "source": 'blah',
//                    "origin": 'blah',
//                    "description": description,
//                    "content-type": 'text/html',
//                    "content": content,
//                    "author": {
//                        "id": 1,
//                        "host": host,
//                        "displayname": "gayoung",
//                        "url": host+"author/gayoung"
//                    },
//                    "categories": "['hello', 'world']",
//                    "comments": [{}],
//                    "pubDate": posttime,
//                    "guid": 'blah',
//                    "visibility": permission
//                    
//                }
//            ]
//        },
//        success: function() {
//            alert("success");
//        },
//        error: function(jqXHR, textStatus, errorThrown) {
//            alert ("AJAX error: "+ jqXHR + ", "+textStatus+", "+errorThrown);
//        }
//    })
//    
//    
//}

function text2form(currentdbId)
{
    // remove overlay with button triggers
        $("#post_overlay-"+currentdbId).unbind("mouseover");
        $("#post_overlay-"+currentdbId).unbind("mouseleave");
        $("#post_overlay-"+currentdbId).css("display", "none");
        
        // get currently displayed contents of the post
        var headerContent = $("#post-"+currentdbId+" h2").first().text();
        var sourceContent = $("#post_source-"+currentdbId).find("span").first().text();
        var originContent = $("#post_origin-"+currentdbId).find("span").first().text();
        var categoryContent = $("#post_category-"+currentdbId).find("span").first().text();
        var description = $("#post_description-"+currentdbId).find("p").first().text();
        var bodyContent = '';
        $("#post_content-"+currentdbId).children().each(function() {
            if(this.tagName != "h2")
            {
                bodyContent += $(this).html();
            }
        });
        var permissionValue = $("#post_permission-"+currentdbId).val();
        
        var editForm = createForm(currentdbId);
        
        $(editForm).insertBefore($("#post-"+currentdbId));
        $("#post-"+currentdbId).css("display", "none");
    
        tinymce.init({
             selector: "#edit_post_content-"+currentdbId,
             plugins: [
                       "advlist autolink lists link image charmap preview anchor",
                       "searchreplace visualblocks code fullscreen",
                       "insertdatetime media table contextmenu paste"
                       ],
             toolbar: "insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image"
        });
    
        tinymce.execCommand('mceRemoveControl', false, "edit_post_content-"+currentdbId);
        tinymce.execCommand('mceAddEditor', true, "edit_post_content-"+currentdbId);
        
        $("#spec_author_div-"+currentdbId).hide();
        
        $("#post_title-"+currentdbId).val(headerContent);
        $("#post_source-"+currentdbId).val(sourceContent);
        $("#post_origin-"+currentdbId).val(originContent);
        $("#post_category-"+currentdbId).val(categoryContent);

        $('select#post_permissions-'+currentdbId).children().each(function() {
            var currentVal = $(this).attr("value");
            if(currentVal.trim() == permissionValue.trim())
            {
                $("#post_permission-"+currentdbId).val(3)
            }
            else
            {
                if($(this).attr("selected") ==  "selected")
                {
                    $(this).removeAttr("selected");
                }
            }
        });
        
        $("#post_description-"+currentdbId).val(description);
        tinymce.get("edit_post_content-"+currentdbId).setContent(bodyContent+" html");
        
}

function createForm(id)
{
    var form = $('<div id="edit_post-'+id+'" class="well">'+
                    '<h3>Edit Post</h3>'+
                    '<form class="form-horizontal" action="" method="POST">'+
                        '<div class="form-group">'+
                            '<label for="post_permissions" class="col-sm-3">Permissions:</label>'+
                            '<div class="col-sm-9">'+
                                '<select id="post_permissions-'+id+'" name="post_permissions-"'+id+' class="col-sm-9 form-control" style="width: 90%;">'+
                                    '<option value="private" selected="selected">Private</option>'+
                                        '<option value="spec_author">Specify</option>'+
                                        '<option value="friends">Friends</option>'+
                                        '<option value="friendsoffriends">Friends of my friends</option>'+
                                        '<option value="local">Friends within my host</option>'+
                                        '<option value="public">Public</option>'+
                                    '</select>'+
                                '</div>'+
                            '</div>'+
                             '<div id="spec_author_div-'+id+'" class="form-group">'+
                                    '<label for="spec_author_input-'+id+'" class="col-sm-3"> Author\'s username:</label>'+
                                    '<div class="col-sm-9">'+
                                        '<input id="spec_author_input-'+id+'" name="spec_author_input-'+id+'" style="width: 90%;" placeholder="Please input the author\'s username."/>'+
                                    '</div>'+
                                '</div>'+
                            '<div class="form-group">'+
                                '<label for="post_title-'+id+'" class="col-sm-3">Title: </label>'+
                                '<div class="col-sm-9">'+
                                    '<input type="text" id="post_title-'+id+'" name="post_title-'+id+'" style="width: 90%;" placeholder="Title of the post"/>'+
                                '</div>'+
                            '</div>'+
                 '<div class="form-group">'+
                    '<label for="post_source-'+id+'" class="col-sm-3">Source of the Post: </label>'+
                    '<div class="col-sm-9">'+
                        '<input type="text" id="post_source-'+id+'" name="post_source-'+id+'" style="width: 90%;" placeholder="Source URI of the post"/>'+
                    '</div>'+
                 '</div>'+
                 '<div class="form-group">'+
                    '<label for="post_origin-'+id+'" class="col-sm-3">Origin of the Post: </label>'+
                    '<div class="col-sm-9">'+
                        '<input type="text" id="post_origin-'+id+'" name="post_origin-'+id+'" style="width: 90%;" placeholder="Origin of the post (URI)"/>'+
                    '</div>'+
                 '</div>'+
                 '<div class="form-group">'+
                    '<label for="post_category-'+id+'" class="col-sm-3">Category of the Post: </label>'+
                    '<div class="col-sm-9">'+
                        '<input type="text" id="post_category-'+id+'" name="post_category-'+id+'" style="width: 90%;" placeholder="(e.g. Medical, Health)"/>'+
                    '</div>'+
                 '</div>'+
                            '<div class="form-group">'+
                                '<label for="post_description-'+id+'" class="col-sm-3">Post Description:</label>'+
                                '<div class="col-sm-9">'+
                                  '<input id="post_description-'+id+'" name="post_description-'+id+'" style="width: 90%;" placeholder="Description of the post"/>'+
                                '</div>'+
                            '</div>'+
                            '<div class="form-group">'+
                                '<label for="edit_post_content-'+id+'" class="col-sm-3">Post Content:</label>'+
                                '<div class="col-sm-9">'+
                                  '<textarea id="edit_post_content-'+id+'" name="edit_post_content-'+id+'" style="width: 90%;"></textarea>'+
                                '</div>'+
                            '</div>'+
                            '<div class="form-group">'+
                                '<label class="col-sm-3"></label>'+
                                '<div class="col-sm-9">'+
                                    '<button class="btn btn-primary btn-md" name="edit" type="submit" width: 10%;">Edit</button>'+
                                    '<button id="edit_cancel" class="btn btn-default btn-md" width: 10%;">Cancel</button>'+
                                '</div>'+
                            '</div>'+
                        '</form>'+
                    '</div>');
    return form;
}