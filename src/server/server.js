var express = require('express');
var path = require('path');
const WebSocket = require('ws');
var http = require('http');
var spawn = require('child_process').spawn;
var active_games = new Map();
var active_connections = new Map();
const client_path = path.join(__dirname, '..', 'client');
const python_script_path = path.join(__dirname, '..', 'game', 'chess', 'chess_for_node.py');

function performPlayerMove(gameID, connID, move, validationString){
    console.log("performPlayerMove. gameID: " + gameID + ", connID: " + connID + ", move: " + move + ", validation: " + validationString);
    
    if (!active_games.has(gameID)){
        //TODO load from memory
        if (!active_connections.has(connID)){
            console.log("PerfromPlayerMove without gameID or connID existing");
            return;
        }
        var socket = active_connections.get(connID);
        var response = {status: 404, validation: validationString, msg: "No game of ID: " + gameID + ", on serverside."}
        socket.send(response);
        console.log("PerfromPlayerMove without gameID existing");
        return;
    }
    var game = active_games.get(gameID);
    var chess = game.chess;
    var humanPlayer = game.humanPlayer;
    var rFrom = move.rFrom;
    var cFrom = move.cFrom;
    var rTo = move.rTo;
    var cTo = move.cTo;

    console.log("Just before starting python script");
    var process = spawn('python', [python_script_path,
        connID, //Not presently being used anywhere
        'move',
        rFrom,
        cFrom,
        rTo,
        cTo,
        chess,
        humanPlayer]);

    process.stdout.on('data', (data) => {
        console.log("Return data from script (player move)");

        let data_obj = JSON.parse(data);
        var socket = active_connections.get(data_obj.id);
        let status = data_obj.status;
        var response = {status: status, id: gameID, validation: validationString, msg: data_obj.msg};
        if (status == 200){
            // response = {status: status, validation: validationString, msg: data_obj.msg};
            console.log("Move success");
            // TODO UPDATE CHESS LIST
            var chess = data_obj.chess;
            var humanPlayer = game.humanPlayer;
            active_games.set(gameID, {chess: chess, humanPlayer: humanPlayer});
            console.log("Server side chess updated");
        } else {
            console.log("Move fail");
        }

        var responseString = JSON.stringify(response);
        socket.send(responseString);
        console.log("response sent: " + responseString);
    });
    //TODO
}

function requestAiMove(gameID, connID){
    console.log("requestAiMove. GameID: " + gameID + ", connID: " + connID);
    if (!active_games.has(gameID)){
        //TODO load from memory
        if (!active_connections.has(connID)){
            console.log("PerfromPlayerMove without gameID or connID existing");
            return;
        }
        var socket = active_connections.get(connID);
        var response = {status: 404, validation: validationString, msg: "No game of ID: " + gameID + ", on serverside."}
        socket.send(response);
        console.log("PerfromPlayerMove without gameID existing");
        return;
    }
    var game = active_games.get(gameID);
    var chess = game.chess; 

    var process = spawn('python', [python_script_path,
        connID, //Not presently being used anywhere
        'ai',
        chess]);
    
    process.stdout.on('data', (data) => {
        let data_obj = JSON.parse(data);
        // let data_obj = JSON.parse(data.toString());
        var socket = active_connections.get(data_obj.id);
        let status = data_obj.status;
        var response = {status: status, id: gameID, move: data_obj.move, msg: data_obj.msg}; // Considder including the validation string stuff
        if (status == 210){
            // response = {status: status, validation: validationString, msg: data_obj.msg};
            console.log("AI move success");
            // TODO UPDATE CHESS LIST
            var chess = data_obj.chess;
            var humanPlayer = game.humanPlayer;
            active_games.set(gameID, {chess: chess, humanPlayer: humanPlayer});
            console.log("Server side chess updated");
        } else {
            console.log("AI move fail");
        }

        var responseString = JSON.stringify(response);
        socket.send(responseString);
        console.log("response sent: " + responseString);
    });  
}

function createNewGame(gameID, connID, humanPlayer){
    console.log("CreateNewGame called with gameID: " + gameID + ", connID: " + connID + ", HumanPlayer: " + humanPlayer);
    if (active_games.has(gameID)){
        if (!active_connections.has(connID)){
            console.log("createNewGame without connID and already existing game ID");
            return;
        }
        var socket = active_connections.get(connID);
        var response = {status: 529, validation: validationString, msg: "No game of ID: " + gameID + ", on serverside."} // Random status code
        socket.send(response);
    }
    // console.log(python_script_path);
    var process = spawn('python', [python_script_path,
        connID, // Not presently being used
        'create']);


    process.stdout.on('data', (data) => {
        console.log("Returned from make new game");
        // console.log(data.toString());
        let data_obj = JSON.parse(data);
        let socket = active_connections.get(data_obj.id);
        let status = data_obj.status;
        let response = {status: status, id: gameID, humanPlayer: humanPlayer, msg: data_obj.msg};
        // TODO: Check data and call appropriate functions
        let chess= data_obj.chess;
        active_games.set(gameID, {chess: chess, humanPlayer: humanPlayer}); // TODO: Potential race condition here
        let responseString = JSON.stringify(response); 
        socket.send(responseString);
        console.log("New game response sent: " + responseString);
    });


    //TODO
}

var app = express();

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

socket.on('connection', ws => {
    
    var connID = (Math.random().toString(36)+'00000000000000000').slice(2, 10);
    while(active_connections.has()){
        connID = (Math.random().toString(36)+'00000000000000000').slice(2, 10);
    }
    ws.connID = connID;
    active_connections.set(connID, ws);
    console.log("Socket connection established with ID: " + connID);
    ws.on('message', message => {
        console.log("Socket message received" + message);
        var jsonMessage = JSON.parse(message);
        var action = jsonMessage.action;

        if (action == 'player move'){
            console.log("TODO: Validate move");
            if (jsonMessage.move){
                performPlayerMove(jsonMessage.id, ws.connID, jsonMessage.move, jsonMessage.validation);
            }
            // response = {status: "done", validation: jsonMessage.validation};
        } else if (action == 'new game'){
            createNewGame(jsonMessage.id, ws.connID, jsonMessage.humanPlayer);
        } else if (action == "ai move") {
            requestAiMove(jsonMessage.id, ws.connID);
        }
        else {
            response = {status: "error"};
        }
    });
  });

// TODO: Let player play as black
// TODO: Considder race conditions
// TODO: Obvious security roblem in just using game ID for everything (e.g. can just try to load a ton of different IDs)
// TODO: Surround parsing in try-catch to avoid server crash when illigeal information fed through sockets.
// TODO: Safeguard against injection attacks in player move