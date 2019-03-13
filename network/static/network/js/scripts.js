
// getting csrf from cookie so ican attach to POST methods
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


$(document).ready(function()
{
  $('#q').typeahead({
    highlight: false,
    minLength: 1
  },
  {
    displayKey: function(suggestion) { 
        if (suggestion.track == undefined) {
         return suggestion.artists + ' (' + suggestion.album + ')';
     }
    else {
        return suggestion.artists + ' - ' + suggestion.track;}},    
    limit: 30,
    source: search,
    templates: {
      suggestion: Handlebars.compile('<div>' + '<img src={{image}}>' + ' {{artists}}'
       + '&emsp;' + '{{track}}' + ' (' + '{{album}}'+ ') ' + '   ' + '{{duration}}'  + '</div>')
    }
        
  });

  // when they select an option, do this
 $('#q').bind('typeahead:select', function(ev, suggestion) {
    
    // submit with ajax so I can get names for the select form of Usernames to who suggest
    $.ajax({
    type: 'POST',
    url: '/getuserstorec',
    data: {
        },
    // on success, add those options to the form select value
    success: function(data, jqXHR){

        $('.toempty').empty();

        // when they select, clear the typeahead with a delay
        //complete form to make a suggestion
        $('#sug').append("<div class='toempty'><textarea rows='5' cols='50' id='msg' name='msg' height='300px' form='sugform'\
            placeholder='Write a message describing this music here'></textarea></div>\
            <div class='toempty' class='input-group'>\
            <select class='form-control' id='recdados' name='recdados'><option value=''\
             selected>Choose Friends</option>\
        <input type='hidden' name='tipo' value='{{ suggestion.tipo }}'>\
        <input type='hidden' name='recdado' id='recdado' value='' />\
        <input type='hidden' class='toempty' name='spotifyuri' value='{{ suggestion.uri }}'>\
        <div style='padding:5px; text-align: center;'><button class='btn btn-outline-secondary' type='submit' id='bton'\
         value='Submit' form='sugform'>Recommend!</button></div></form></div>");
        //get a loop to insert recdado suggestions in the select form
        var i;
        for (i=0; i < data.length; i++){
            $('#recdados').append("<option value='" + data[i].names + "' data-imagesrc='"+data[i].img+"'>" + data[i].names + "</option>")
        }
        $('#recdados').append("<option value='everyone'>Every friend!</option></select>")

        var embed = suggestion.embedurl
        var urlembed = embed.split(".com/")
        $('#displayrec').html('<iframe src="' + urlembed[0] + 
        ".com/embed/" + urlembed[1] + '"' + ' width="300" height="380" \
        frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>');
       
    }

});
    
    
  // need to format the url so I can embed for sample
  
   $(function() {
    var forminfo = $('#sugforminfo');

    // event listener so i can stop the broswer from sbumitting and save the data
    $('#sugform').submit(function(event) {    
    event.preventDefault();


    var datastring = $("#sugform").serialize()
    // submit with ajax
    $.ajax({
    type: 'POST',
    url: '/listento',
    data: {
        'recdado' : $('#recdados').val(),
        'spotifyuri' : suggestion.uri,
        'msg' : $('#msg').val(),
        'tipo': suggestion.tipo,

    },
    // if it runs, get a URL so user can share and refresh page with alert
    success: function(data, jqXHR){

        //$("#genurl").html("Send this link to people!" + genurl);
        $(".toempty").empty();

         // when they select, clear the typeahead with a delay
        setTimeout(function(){$('#q').typeahead('val', '');}, 500);

        new ClipboardJS('.btn');


        //get a text box with a copy to clipboard button
        $("#genurl").append('<div class="input-group mb-3 shadow-textarea toempty ">\
            <div align="middle" class="input-group-prepend shadow-textarea">\
            <textarea class="form-control" style="max-width:600px;" id="copy" rows="1" cols="40" >https://recspotify.herokuapp.com/listentothis/'+ data.genurl + '</textarea></div>\
            <button class="btn btn-outline-secondary" data-clipboard-target="#copy">\
            COPY</button><p style="padding:12px">Share this link! (if you selected\
            a friend, he can see it now too)</p></div><br>')
        
    }

}).done(function(response) {
 
    // Clear the form.
    $('#msg').val('');
    $('#recdado').val('');
}).fail(function(data) {

    // Make sure that the formMessages div has the 'error' class.
   

    // Set the message text.
    if (data.responseText !== '') {
        $(sug).text(data.responseText);
    } else {
        $(sug).text('Oops! An error occured and your message could not be sent.');
    }
}); // function for fail ajax

});
}); // function for form
}); //selection


        
 
    



}); //doc ready


function search(query, syncResults, asyncResults)
{
    // Get places matching query (asynchronously)
    let parameters = {
        q: query
    };
    $.getJSON("/search", parameters, function(data, textStatus, jqXHR) {

        // Call typeahead's callback with search results (i.e., places)
        asyncResults(data);
    });
}

function listento(query, syncResults, asyncResults)
{
    // Get places matching query (asynchronously)
    let parameters = {
        q: query
    };
    $.getJSON("/listento", parameters, function(data, textStatus, jqXHR) {

        // Call typeahead's callback with search results (i.e., places)
        asyncResults(data);
    });
}







