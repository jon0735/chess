
$(document).ready(() =>{
    console.log("Welcome to the main page");

    document.getElementById("toChess").addEventListener("click", () => {
        // console.log("Button clicked");
        // console.log("window.location.href" + window.location.href);
        // console.log("document.URL" + document.URL);
        // console.log("window.location.host" + window.location.host); 
        // console.log("window.location.origin" + window.location.origin); 
        // console.log("window.location.pathname.split( '/' )" + window.location.pathname.split( '/' ));
        window.location.href = window.location.href + 'chess';

        // var xhttp = new XMLHttpRequest();
        // xhttp.open('GET', document.URL + "chess");
    });
});

// var base_url = window.location.origin;

// var host = window.location.host;

// var pathArray = window.location.pathname.split( '/' );