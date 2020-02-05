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

    if (!active_games.has(gameID)){
        //TODO load from memory
        if (!active_connections.has(connID)){
            console.log("PerfromPlayerMove without gameID or connID existing");
            return;
        }
        var socket = active_connections.get(connID);
        var response = {status: 404, validation: validationString, msg: "No game of ID: " + gameID + ", on serverside."}
        socket.send(JSON.stringify(response));
        console.log("PerfromPlayerMove without gameID existing");
        return;
    }
    var game = active_games.get(gameID);
    // var chess = game.chess;
    // var humanPlayer = game.humanPlayer;
    // var rFrom = move.rFrom;
    // var cFrom = move.cFrom;
    // var rTo = move.rTo;
    // var cTo = move.cTo;
    var promote = move.promote;
    if (promote == null){
        promote = 0;
    }

    console.log("Just before starting python script");
    var process = spawn('python', [python_script_path,
        connID, //Not presently being used anywhere
        'move',
        move.rFrom,
        move.cFrom,
        move.rTo,
        move.cTo,
        game.chess,
        game.humanPlayer,
        promote]);

    process.stdout.on('data', (data) => { handleScriptData(data, gameID, connID, game.humanPlayer); });
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
    // var humanPlayer = game.humanPlayer;

    // TODO include 'HumanPlayer' argument to prevent player from just getting ai arg (Or is that ok?)
    var process = spawn('python', [python_script_path,
        connID, //Not presently being used anywhere
        'ai',
        chess]);
    
    process.stdout.on('data', (data) => { handleScriptData(data, gameID, connID, game.humanPlayer); });  
}

function createNewGame(gameID, connID, humanPlayer){
    console.log("CreateNewGame called with gameID: " + gameID + ", socket: " + connID + ", HumanPlayer: " + humanPlayer);
    if (active_games.has(gameID)){
        var response = {status: 529, validation: validationString, msg: "No game of ID: " + gameID + ", on serverside."} // Random status code
        socketID.send(response);
    }
    var process = spawn('python', [python_script_path,
        gameID, // Not presently being used
        'create']);

    
    process.stdout.on('data', (data) => { handleScriptData(data, gameID, connID, humanPlayer); });
}

function handleScriptData(data, gameID, connID, humanPlayer){
    let dataObj = JSON.parse(data);
    let status = dataObj.status;
    var response = {status: status, id: gameID, msg: dataObj.msg}; // Consider including the validation string stuff
    if (status == 200 || status == 210){ // TODO switch statement?
        console.log("Move success");
        response.move = dataObj.move;
        var chess = dataObj.chess;
        active_games.set(gameID, {chess: chess, humanPlayer: humanPlayer});
        console.log("Server side chess updated");
    } else if (status == 201) {
        response.humanPlayer = humanPlayer;
        let chess = dataObj.chess;
        active_games.set(gameID, {chess: chess, humanPlayer: humanPlayer});
        console.log("New game created");
    } else if (status == 500) {
        console.log("Move failed (Error). Msg: " + response.msg);
        response.msg = "Server error encountered. I.e. server has a bug";
    } else {
        console.log("Script return status: " + response.status + ", msg: " + response.msg);
    }

    var responseString = JSON.stringify(response);
    var socket = active_connections.get(connID);
    if (socket != null){
        socket.send(responseString);
        console.log("response sent: " + responseString);
    } else {
        console.log("No active socket to respond to");
    }
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

var webSocketServer = new WebSocket.Server( {server} );

server.listen(8210, () => {
    var host = server.address().address;
    var port = server.address().port;

    console.log('Listening: ', host, port);
});

webSocketServer.on('connection', ws => {
    // TODO change from id stuff, to just send socket along as argument
    var connID = (Math.random().toString(36)+'00000000000000000').slice(2, 10); // random id
    while(active_connections.has(connID)){
        connID = (Math.random().toString(36)+'00000000000000000').slice(2, 10); // random id again if colision
    }
    ws.connID = connID;
    active_connections.set(connID, ws);
    console.log("Socket connection established with ID: " + connID);
    ws.on('message', message => {
        try {
            console.log("Socket message received: " + message);
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
                var response = {status: 501, msg: "action '" + action + "' not recognised"};
                ws.send(JSON.stringify(response));
            }
        } catch (error){
            console.log("Error from incomming message. Error: " + error + ": " + error.stack);
            var response = {status: 501, msg: "Server error encountered. Most likely due to nonsense message sent to server"};
            ws.send(JSON.stringify(response));
        }
    });
  });

// TODO: Let player play as black
// TODO: Consider race conditions (is this even a thing in javascript async?)
// TODO: Obvious security roblem in just using game ID for everything (e.g. can just try to load a ton of different IDs) (probably wont do anything about this)
// TODO: Surround parsing in try-catch to avoid server crash when illigeal information fed through sockets. (done)
// TODO: Safeguard against injection attacks in player move

// Codes:
// 200 - Succesful player rmove
// 201 - Game created
// 202 - Move made (ai or player) which led to game ending
// 210 - Succesful ai move
// 220 - promotion argument needed
// 400 - Illegal move
// 500 - Parsing error in the python script
// 501 - Generic server error
// 529 - No such game ID on the server side