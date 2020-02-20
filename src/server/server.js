var express = require('express');
var path = require('path');
const WebSocket = require('ws');
var http = require('http');
var spawn = require('child_process').spawn;
var activeGames = new Map();
var activeConnections = new Map();
const clientPath = path.join(__dirname, '..', 'client');
// const pythonScriptPath = path.join(__dirname, '..', 'game', 'test.py');
const pythonScriptPath = path.join(__dirname, '..', 'game', 'chess', 'chess_for_node.py');

// Calls python script based on the requested client move
function performPlayerMove(gameID, connID, move, validationString){

    if (!activeGames.has(gameID)){
        //TODO: load from memory
        if (!activeConnections.has(connID)){
            console.log("PerfromPlayerMove without gameID or connID existing");
            return;
        }
        var socket = activeConnections.get(connID);
        var response = {status: 404, validation: validationString, msg: "No game of ID: " + gameID + ", on serverside."}
        socket.send(JSON.stringify(response));
        console.log("PerfromPlayerMove without gameID existing");
        return;
    }

    var game = activeGames.get(gameID);
    var promote = move.promote;
    if (promote == null){
        promote = 0;
    }

    var process = spawn('python', [pythonScriptPath,
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
    if (!activeGames.has(gameID)){
        //TODO load from memory
        if (!activeConnections.has(connID)){
            console.log("PerfromPlayerMove without gameID or connID existing");
            return;
        }
        var socket = activeConnections.get(connID);
        var response = {status: 404, validation: validationString, msg: "No game of ID: " + gameID + ", on serverside."}
        socket.send(response);
        console.log("PerfromPlayerMove without gameID existing");
        return;
    }
    var game = activeGames.get(gameID);
    var chess = game.chess;

    // TODO include 'HumanPlayer' argument to prevent player from just getting ai arg (Or is that ok?)
    var process = spawn('python', [pythonScriptPath,
        connID, //Not presently being used anywhere
        'ai',
        chess]);
    
    process.stdout.on('data', (data) => { handleScriptData(data, gameID, connID, game.humanPlayer); });  
}

function createNewGame(gameID, connID, humanPlayer){
    console.log("CreateNewGame called with gameID: " + gameID + ", socket: " + connID + ", HumanPlayer: " + humanPlayer);
    if (activeGames.has(gameID)){
        var response = {status: 528, msg: "ID: " + gameID + ", already in use."} // Random status code
        if (!activeConnections.has(connID)){
            console.log("No connection to return new game error message to.");
            return;
        }
        var socket = activeConnections.get(connID);
        socket.send(JSON.stringify(response));
        return;
    }
    var process = spawn('python', [pythonScriptPath,
        gameID, // Not presently being used
        'create']);
    console.log("After spawn new game");
    console.log(pythonScriptPath);
    process.stdout.on('data', (data) => { handleScriptData(data, gameID, connID, humanPlayer); });
    console.log("After on settings");
}

function loadGame(gameID, connID){
    console.log("LoadGame called with gameID: " + gameID + ", connID: " + connID);
    if (!activeGames.has(gameID)) {
        var response = {status: 529, msg: "No game of ID: " + gameID + ", on serverside."} // Random status code
        if (!activeConnections.has(connID)){
            console.log("No connection to return new game error message to.");
            return;
        }
        var socket = activeConnections.get(connID);
        socket.send(JSON.stringify(response));
        return;
    } 
    
    var game = activeGames.get(gameID);
    var humanPlayer = game.humanPlayer;
    var chessString = game.chess;
    var chessObject = JSON.parse(chessString);
    var response = {status: 202, id: gameID, board: chessObject.board, turn: chessObject.turn_num, inTurn: chessObject.in_turn, humanPlayer: humanPlayer, msg: "Succesfully loaded"};
    
    var socket = activeConnections.get(connID);
    if (socket != null) {
        socket.send(JSON.stringify(response));
    } else {
        console.log("Cant return load, due to non existing connection");
    }
}

function handleScriptData(data, gameID, connID, humanPlayer){
    console.log("Handlescriptdata");
    var dataObj;
    try {
        dataObj = JSON.parse(data);
    } catch (error){
        dataObj = {status: 500, msg: "Shit happened in server script"}
        console.log("Error in json parsing");
        console.log(data.toString());
        console.log(error);
    }
    // let dataObj = JSON.parse(data);
    let status = dataObj.status;
    var response = {status: status, id: gameID, msg: dataObj.msg}; // Consider including the validation string stuff
    switch (status) {
        case 200: // Legal player move
        case 210: // legal ai move
            console.log("Move success");
            response.move = dataObj.move;
            var chess = dataObj.chess;
            activeGames.set(gameID, {chess: chess, humanPlayer: humanPlayer});
            console.log("Server side chess updated");
            break;
        case 201: // game created
            response.humanPlayer = humanPlayer;
            var chess = dataObj.chess;
            activeGames.set(gameID, {chess: chess, humanPlayer: humanPlayer});
            console.log("New game created");
            break;
        case 203: // legal move that resulted in the game concluding (/win/lose/draw)
            console.log("Game ended");
            response.move = dataObj.move;
            response.winner = dataObj.winner;
            activeGames.delete(gameID);
            console.log("Game deleted from active games. ID: " + gameID);
            console.log(activeGames);
            break;
        case 220: // promotion arg needed for move to be legal
            console.log("Promotion arg needed");
            break;
        case 400: // illegal move
            console.log("Illegal move");
            break;
        case 500: // Error when trying to run python script
            console.log("Move failed (Error). Msg: " + response.msg);
            response.msg = "Server error encountered. I.e. server has a bug";
            break;
        default: // Other weird stuff
            console.log("Script return status: " + response.status + ", msg: " + response.msg);
    }

    var responseString = JSON.stringify(response);
    var socket = activeConnections.get(connID);
    if (socket != null){
        socket.send(responseString);
        console.log("response sent: " + responseString);
    } else {
        console.log("No active socket to respond to");
    }
}

var app = express();

app.use(express.static(clientPath));

app.get('/', function (req, res){
    res.sendFile(path.join(clientPath, 'index.html'));
    console.log("Get request for index received");
});

app.get('/chess', function (req, res){
    res.sendFile(path.join(clientPath, 'chess.html'));
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
    // TODO: change from id stuff, to just send socket along as argument (maybe not. Gives weird reference error when trying)
    var connID = (Math.random().toString(36)+'00000000000000000').slice(2, 10); // random id
    while(activeConnections.has(connID)){
        connID = (Math.random().toString(36)+'00000000000000000').slice(2, 10); // random id again if colision
    }
    ws.connID = connID;
    activeConnections.set(connID, ws);
    console.log("Socket connection established with ID: " + connID);
    ws.on('message', message => {
        try {
            console.log("Socket message received: " + message);
            var jsonMessage = JSON.parse(message);
            var action = jsonMessage.action;
            switch (action) {
                case 'player move':
                    performPlayerMove(jsonMessage.id, ws.connID, jsonMessage.move, jsonMessage.validation);
                    break;
                case 'new game':
                    createNewGame(jsonMessage.id, ws.connID, jsonMessage.humanPlayer);
                    break;
                case 'ai move':
                    requestAiMove(jsonMessage.id, ws.connID);
                    break;
                case 'load game':
                    loadGame(jsonMessage.id, ws.connID);
                    break;
                default:
                    var response = {status: 501, msg: "action '" + action + "' not recognised"};
                    ws.send(JSON.stringify(response));
            }
        } catch (error) {
            console.log("Error from incomming message. Error: " + error + ": " + error.stack);
            var response = {status: 501, msg: "Server error encountered. Most likely due to nonsense message sent to server"};
            ws.send(JSON.stringify(response));
        }
    });
  });

// TODO: Let player play as black
// TODO: Obvious security roblem in just using game ID for everything (e.g. can just try to load a ton of different IDs) (probably wont do anything about this)
// TODO: Loading game from one tab, while being played from other tab, desyncs one instance (probably wont deal with this)
// TODO: Surround parsing in try-catch to avoid server crash when illigeal information fed through sockets. (done)
// TODO: Safeguard against injection attacks in player move
// TODO: Go through this and client script removing or implementing validation string stuff

// Codes:
// 200 - Succesful player rmove
// 201 - Game created
// 202 - Game loaded
// 203 - Move made (ai or player) which led to game ending
// 210 - Succesful ai move
// 220 - promotion argument needed
// 400 - Illegal move
// 500 - Parsing error in the python script
// 501 - Generic server error
// 528 - Illegal game ID (already in use)
// 529 - No such game ID on the server side