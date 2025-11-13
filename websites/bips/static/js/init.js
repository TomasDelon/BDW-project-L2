
window.onload = function() {
    /*
    Initialization function
    */
   /* initialize panel of old/previous queries */
    var div = document.getElementById("panel-log-queries");
    var overlay = document.getElementById('background-overlay');
    document.onclick = function(e){
        if(e.target.id == 'background-overlay'){
            div.style.display = 'none';
            overlay.style.display = 'none';
        }
    }
}


function toggle_log_panel() {
  /*
  ** Show or hide the panel of old/previous queries
  */
  var div = document.getElementById("panel-log-queries");
  var overlay = document.getElementById('background-overlay');
  style_div = window.getComputedStyle(div);
  if(style_div.display == "none") {  // div is not visible, show it
    div.style.display = "block";
    overlay.style.display = 'block';
  }
  else { // div is visible, hide it
    div.style.display = "none";
    overlay.style.display = 'none';
  }
}


/* if in SQL form, enables the form to be submitted with Ctrl-Enter */
var textarea_requete_sql = document.getElementById('textarea_requete_sql');
if(textarea_requete_sql != null) {  // add event for Ctrl-Enter in textarea
  document.getElementById('textarea_requete_sql').addEventListener('keydown', (event) => {
    if(event.key === "Enter" && (event.metaKey || event.ctrlKey)) {  // Ctrl and Enter keys
      document.getElementById('form_requete_sql').submit();
    }
  });
}