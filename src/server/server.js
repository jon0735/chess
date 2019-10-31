var express = require('express');
var path = require('path');
const WebSocket = require('ws');
var http = require('http');

var app = express();

const client_path = path.join(__dirname, '..', 'client');

app.use(express.static(client_path));

app.get('/', function (req, res){
    res.sendFile(path.join(client_path, 'index.html'));
    console.log("Get request for index received");
});

app.get('/chess', function (req, res){
    res.sendFile(path.join(client_path, 'chess.html'));
    console.log("Get request for chess received");
});

const server = http.createServer(app);

var socket = new WebSocket.Server( {server} );

server.listen(8210, () => {
    var host = server.address().address;
    var port = server.address().port;

    console.log('Listening: ', host, port);
});

// var server = app.listen(8210, function (){
//     var host = server.address().address;
//     var port = server.address().port;

//     console.log('Listening: ', host, port);
// });

socket.on('connection', ws => {
    console.log("Socket connection established");
    ws.on('message', message => {
        console.log("Socket message received" + message);
        var jsonMessage = JSON.parse(message);
        console.log("TODO: Validate move");
        var response = {status: "done", validation: jsonMessage.validation};
        ws.send(JSON.stringify(response));
    //   var json = JSON.parse(message);
    //   console.log(json);
    //   sendstuff(json.deviceId, json.led, json.value );
    });
  })

