
// global variables/constants
const squareLength = 80; // MUST be 80 or integer stuff and images will break down. TODO: fix
const lineWidth = 2;
var globalChess = null;
var selectedPiece = null;
var id = null;
var boardStartX;
var boardStartY;
var waiting = false;
var webSocket;
var moveInProgress; // TODO: Deal with this. Is used inconsistently

// Chess class for client side. Contains no move rules and the like. That is handled serverside
class Chess {
    constructor(humanPlayer, board, inTurn, turnNum){
        if (board === undefined){ board = getStartBoard(); }
        if (humanPlayer === undefined){ humanPlayer = 1; }
        if (inTurn === undefined){ inTurn = 1; }
        if (turnNum === undefined){ turnNum = 1; }
        this.board = board;
        this.inTurn = inTurn;
        this.humanPlayer = humanPlayer;
        this.turnNum = turnNum;
    }

    // Performs chess move. Updating globalchess, and moving/changing html elements
    // No checks for if move is legal. That is handled server side.
    move(move){
        var rFrom = move.rFrom;
        var cFrom = move.cFrom;
        var rTo = move.rTo;
        var cTo = move.cTo;
        var promote = move.promote;
        var enPassant = move.enPassant;
        var castle = move.castle;
        if(this.board[rFrom][cFrom] == null){
            console.log("Attempted move on non existant piece")
            return;
        }
        var movedPiece = this.board[rFrom][cFrom];
        var htmlElement = movedPiece.htmlElement;
        htmlElement.style.outline = 'none';
        var toPiece = this.board[rTo][cTo];
        if (toPiece != null && toPiece.htmlElement != null){
             toPiece.htmlElement.parentNode.removeChild(toPiece.htmlElement);
        }
        
        this.board[rFrom][cFrom] = null;
        movedPiece.row = rTo;
        movedPiece.column = cTo;
        this.board[rTo][cTo] = movedPiece;
        selectedPiece = null; // TODO: Figure out if this is needed still
        moveElementCell(htmlElement, rTo, cTo);
        if (promote != null) {
            var type;
            // var team = movedPiece.team;
            if (promote == 2){
                type = 'R';
            } else if (promote == 3) {
                type = 'N';
            } else if (promote == 4) {
                type = 'B';
            } else if (promote == 10) {
                type = 'Q';
            } else {
                console.log("FATAL ERROR: Illegal promote arg: " + promote);
                return;
            }

            setTimeout( () => {  // Timeout to allow move animation to finish before changing piece due to promotion
                deleteHtmlPiece(this, rTo, cTo);
                this.board[rTo][cTo] = new Piece(type, movedPiece.team, rTo, cTo);
                var offset = document.getElementById("board_div").getBoundingClientRect();
                var top = offset.top;
                var left = offset.left;
                drawHtmlPiece(this, rTo, cTo, top, left);
            }, 150); // Animation time for pawn to move 1 square is 100. This should give enough time to look passable
        }
        if (enPassant != null) {
            setTimeout( () => {
                var row = enPassant[0];
                var column = enPassant[1];
                deleteHtmlPiece(this, row, column);
                this.board[row][column] = null;
            }, 200);
            console.log("Handle En Passant");
        }
        if (castle != null){
            var rookMove = {
                rFrom: castle[0][0],
                cFrom: castle[0][1],
                rTo: castle[1][0],
                cTo: castle[1][1],
                promote: null,
                enPassant: null,
                castle: null};
            this.move(rookMove); // May need changing based on future chess state changes (turn number e.g.)
        } else { // castling moves calls recursively once. Having these two state updates in else, ensures game state is only updated once
            this.turnNum++;
            this.inTurn = this.inTurn * -1;

        }
    }
}

// piece class. Contains relevant information for piece, and a pointer to corresponding html element (if such exists)
class Piece {
    constructor(type, team, row, column, htmlElement){
        this.type = type;
        this.team = team;
        this.row = row;
        this.column = column;
        if (htmlElement === undefined){
            this.htmlElement = null;
        } else {
            this.htmlElement = htmlElement;
        }
    }
}

function getStartBoard(){
    var board = [...Array(8)].map(e => Array(8));  // Creates 8x8 array with undefined values
    for (var r = 2; r < 6; r++){
        for (var c = 0; c < 8; c++){
            board[r][c] = null;
        }
    }
    for (var c = 0; c < 8; c++){
        board[1][c] = new Piece('P', 1, 1, c);
    }
    for (var c = 0; c < 8; c++){
        board[6][c] = new Piece('P', -1, 6, c);
    }
    board[0][0] = new Piece('R', 1, 0, 0);
    board[0][1] = new Piece('N', 1, 0, 1);
    board[0][2] = new Piece('B', 1, 0, 2);
    board[0][3] = new Piece('Q', 1, 0, 3);
    board[0][4] = new Piece('K', 1, 0, 4);
    board[0][5] = new Piece('B', 1, 0, 5);
    board[0][6] = new Piece('N', 1, 0, 6);
    board[0][7] = new Piece('R', 1, 0, 7);

    board[7][0] = new Piece('R', -1, 7, 0);
    board[7][1] = new Piece('N', -1, 7, 1);
    board[7][2] = new Piece('B', -1, 7, 2);
    board[7][3] = new Piece('Q', -1, 7, 3);
    board[7][4] = new Piece('K', -1, 7, 4);
    board[7][5] = new Piece('B', -1, 7, 5);
    board[7][6] = new Piece('N', -1, 7, 6);
    board[7][7] = new Piece('R', -1, 7, 7);
    return board;
}

// Deletes all html elements for the pieces in the given chess object
function deleteHtmlPieces(chess){
    console.log("Delete pieces called");
    if (chess == null){
        console.log("Chess is null");
        return;
    }
    var board = chess.board;
    for (var r = 0; r < 8; r++){
        for (var c = 0; c < 8; c++){
            var piece = board[r][c];
            if (piece == null){
                continue;
            }
            var htmlElement = piece.htmlElement;
            if (htmlElement == null){
                continue;
            }
            htmlElement.parentNode.removeChild(htmlElement);
            piece.htmlElement = null;
        }
    }
}

// deletes single piece html object
function deleteHtmlPiece(chess, r, c){
    var board = chess.board;
    var piece = board[r][c];
    if (piece == null){
        console.log("Piece is null. Continuing");
        return;
    }
    var htmlElement = piece.htmlElement;
    if (htmlElement == null){
        console.log("Html element is null. Continuing");
        return;
    }
    htmlElement.parentNode.removeChild(htmlElement);
    piece.htmlElement = null;
    // console.log("Piece deleted");
}

//Creates and draws html elements corresponding to all pieces in given chess object
function drawHtmlPieces(chess){ // should always call deleteHtmlPieces before
    var offset = document.getElementById("board_div").getBoundingClientRect();
    var top = offset.top;
    var left = offset.left;
    for (var r = 0; r < 8; r++){
        for (var c = 0; c < 8; c++){
            drawHtmlPiece(chess, r, c, top, left);
        }
    }
}

function drawHtmlPiece(chess, r, c, top, left){
    var board = chess.board;
    var piece = board[r][c];
    if (piece == null){
        return;
    }
    var htmlElement = piece.htmlElement;
    if (htmlElement == null){ // If piece does not already have an html element attached
        var pieceImg = document.createElement('img');
        pieceImg.src = "resources/" + getPieceImageName(piece);
        pieceImg.style.transitionTimingFunction = "linear";
        pieceImg.style.zIndex = 1;
        pieceImg.style.position = "absolute";
        pieceImg.style.left = Math.round(left + 0.5 * lineWidth + squareLength * (c + .5));
        pieceImg.style.top = Math.round(top + 0.5 * lineWidth + squareLength * (7.5 - r));
        document.getElementById("chess_div_right").appendChild(pieceImg);
        piece.htmlElement = pieceImg;
    } else { 
        console.log("Existing Piece found while drawing. Someone fucked up");
    }
    // add event listeners to created pieces
    if (piece.team == chess.humanPlayer){
        piece.htmlElement.addEventListener('click', ownPieceEventHandler);
    } else {
        piece.htmlElement.addEventListener('click', enemyPieceEventHandler);
    }
    piece.htmlElement.piece = piece;
}

// event handler for non human player pieces
function enemyPieceEventHandler(event){
    if (waiting){
        console.log("Move in progress. Wait before doing more shit");
        return;
    }
    var htmlPiece = event.target;
    var piece = htmlPiece.piece;

    if (selectedPiece != null){
        console.log("Attempt move");
        var move = {
            rFrom: selectedPiece.row,
            cFrom: selectedPiece.column,
            rTo: piece.row,
            cTo: piece.column,
            promote: null,
            enPassant: null,
            castle: null};
            attemptMove(move);
    }
}

// event handler for human player pieces
function ownPieceEventHandler(event){
    if (waiting){
        console.log("Move in progress. Wait before doing more shit");
        return;
    }
    // waiting = true;
    var htmlPiece = event.target;
    htmlPiece.style.zIndex = 5;
    var piece = htmlPiece.piece;
    // console.log("r = " + piece.row + ", c = " + piece.column);
    if (selectedPiece != null){
        selectedPiece.htmlElement.style.outline = 'none';
    }
    if (piece == selectedPiece) {
        selectedPiece = null;
        htmlPiece.style.zIndex = 1;
        return;
    } 
    htmlPiece.style.outline = '2px solid red'
    // htmlPiece.style.backgroundColor = "#FDFF47";
    selectedPiece = piece;
    // waiting = false;
}

// event handler for chess board. I.e. any place on board which is not hidden by a chess peice html object
function boardEventHandler(event){
    if (waiting){
        console.log("Move in progress. Wait before doing more shit");
        return;
    }
    var rect = event.target.getBoundingClientRect();
    var x = event.clientX - rect.left; //x position within the element.
    var y = event.clientY - rect.top;  //y position within the element.
    if (event.clientX < boardStartX || event.clientY < boardStartY){
        return;
    }
    if ((globalChess == null) || (selectedPiece == null)){
        return;
    }
    // var rTo = Math.floor(8 - (event.clientY - boardStartY) / squareLength);
    // var cTo = Math.floor((event.clientX - boardStartX) / squareLength);
    var rTo = Math.floor(8 - (y - .5 * squareLength) / squareLength);
    var cTo = Math.floor((x - .5 * squareLength) / squareLength);
    var rFrom = selectedPiece.row;
    var cFrom = selectedPiece.column;
    var move = {rFrom: rFrom,
        cFrom: cFrom,
        rTo: rTo,
        cTo: cTo,
        promote: null,
        enPassant: null,
        castle: null};
    attemptMove(move);
}

// Translates board (array with 8 arrays of length 8) indexing arguments to standard chess notation
function rowColumnToChessNotation(row, column){
    var letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    return [letters[column], row + 1];
}

// send information to server to handle an attempted move
function attemptMove(move){
    waiting = true;
    moveInProgress = move;
    var boardString = boardToString(globalChess.board);

    // TODO: validation string is used for nothing presently. Reconsider if it should just be deleted
    var validation = {boardString: boardString, 
                      inTurn: globalChess.inTurn,
                      humanPlayer: globalChess.humanPlayer}; 
    var message = {action: 'player move',  // codes might be more efficient (but will lower readability)
                   move: move,
                   id: id,
                   validation: validation}
    webSocket.send(JSON.stringify(message));
    // finishMove();
}

// Includes promotion argument in last attempted move
// If move was illegal due to lacking promotion argument this will be called
function promotionMove(promote){
    moveInProgress.promote = promote;
    attemptMove(moveInProgress);
}

// Perform move on globalchess, and update various UI elements 
// Will be called after succesful move has been performed on server, and response have been received by client
function finishMove(move){
    console.log("Finish move called");
    globalChess.move(move);
    if (globalChess.inTurn == globalChess.humanPlayer) { waiting = false; }
    document.getElementById("turnNum").innerHTML = globalChess.turnNum;
    var inTurn;
    if (globalChess.inTurn == 1){ inTurn = "White"; }
    else {inTurn = "Black";}
    document.getElementById("inTurn").innerHTML = inTurn;

    // waiting = false;
    // console.log("TODO: finish move stuff");
}

// Translates board to a simple stringbased representation
// Has probably been made superflous by resent changes
function boardToString(board){
    var s = '';
    for(var r = 0; r < 8; r++){
        for(var c = 0; c <8; c++){
            var piece = board[r][c];
            var type;
            if (piece == null){
                type = "x";
            } else {
                type = piece.type;
                if (piece.team == -1){
                    type = type.toLowerCase();
                }
            }
            s += type;
        }
    }
    return s;
}

// Returns the name of the png image corresponding to that kind of piece. 
// Used when creating html elements corresponding to chess pieces
function getPieceImageName(piece){
    var type = piece.type;
    var team = piece.team;
    // console.log("getPieceImageName with type = " + type + ", colour = " + team);
    var typeString = "";
    if (type == "P"){
        typeString = "Pawn";
    } else if (type == "N"){
        typeString = "Knight";
    } else if (type == "B"){
        typeString = "Bishop";
    } else if (type == "R"){
        typeString = "Rook";
    } else if (type == "Q"){
        typeString = "Queen";
    } else if (type == "K"){
        typeString = "King";
    } else{
        console.log("Type " + type + ", not recognised. Shit will now happen");
    }
    var colourString = "";
    if (team == 1){
        colourString = "White";
    } else if (team == -1){
        colourString = "Black";
    } else {
        console.log("Colour " + team + ", not recognised. Shit will now happen");
    }
    return typeString + "_" + colourString + ".png";
}

// Move html piece element from whereever it presently is to row 'r' and column 'c'
function moveElementCell(element, r, c){
    console.log("MoveElementCell called", r, c);
    var toX = Math.round(c * 80 + boardStartX - 1);
    var toY = Math.floor((7 - r) * 80 + boardStartY);
    console.log("X: ", toX);
    console.log("Y: ", toY);
    moveElement(element, toX, toY);
}

// Move html piece element from whereever it presently is to given x and y coordinaters
function moveElement(element, toX, toY){
    var startX = parseInt(element.style.left);
    var startY = parseInt(element.style.top);
    var xDist = toX - startX;
    var yDist = toY - startY;
    var dist = Math.sqrt(xDist * xDist + yDist * yDist)
    var animationTime = Math.floor(dist/.8); // dist/800 -> 0.1s per square (80px) ish

    element.style.transitionTimingFunction = "linear";
    element.style.transitionDuration = "" + animationTime + "ms"; 
    element.style.top = toY;
    element.style.left = toX;
    setTimeout(() => { // Timeout to allow animation to finish before changing z-index
        element.style.zIndex = 1;
        element.style.transitionDuration = "0s";
    }, animationTime);
}

/**
 * Draws chess board on canvas. Numbering and all. Only board. No pieces.
 * @param {Canvas} canvas Pretty self explanatory
 */
function drawChessBoard(canvas){
    canvas.width = 2 * lineWidth + 8.5 * squareLength;
    canvas.height = 2 * lineWidth + 8.5 * squareLength;

    var context = canvas.getContext("2d");
    context.font = "" + squareLength * .5 + "px Arial";
    context.textAlign = "center";
    var letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    for (var c = 0; c < 8; c++){
        context.fillText(letters[c], squareLength * (c + 1), .5 * squareLength - 4 * lineWidth);
    }
    for (var r = 0; r < 8; r++){
        context.fillText('' + (r + 1), 0.25 * squareLength - 3 * lineWidth , (8 - r) * squareLength + .25 * squareLength - 3 * lineWidth );
    }

    context.beginPath();
    context.rect( .5 * squareLength, .5 * squareLength, 8 * squareLength + lineWidth, 8 * squareLength + lineWidth);
    context.strokeStyle = "black";
    context.lineWidth = lineWidth;
    context.stroke();
    for(var i = 0; i < 8; i++){
        for(var j = 0; j < 8; j++){
                context.beginPath();
                context.rect((i + .5) * squareLength +  0.5 * lineWidth, (j + .5) * squareLength + 0.5 * lineWidth, squareLength, squareLength);
                var colour = "grey";
                if ((i + j) % 2 == 0){
                    colour = "white";
                }
                context.fillStyle = colour;
                context.fill();
        }
    }
}

// Sets up all UI and state corresponding to a completely new game
function beginNewGame(newID, humanPlayer){
    id = newID;
    if (chess != null){
        deleteHtmlPieces(chess);
    }
    var chess = new Chess(humanPlayer);
    drawHtmlPieces(chess);
    globalChess = chess;
    setUiInfo(newID, globalChess);
    waiting = false;
}

// Sets up all UI and state corresponding to a loaded game
function loadGame(gameID, pyBoard, turnNum, humanPlayer, inTurn){
    id = gameID;
    var board = pythonToJsBoard(pyBoard);
    deleteHtmlPieces(globalChess);
    globalChess = new Chess(humanPlayer, board, inTurn, turnNum);
    drawHtmlPieces(globalChess);
    setUiInfo(gameID, globalChess);
    if (inTurn != humanPlayer) { waiting = true; } 
    else { waiting = false; }
}

// sets Game Info html stuff such that it aligns with the given gameID and chess object
function setUiInfo(gameID, chess){
    console.log("SetUiInfor called with ID: " + gameID);
    document.getElementById("id").innerHTML = gameID;
    document.getElementById("turnNum").innerHTML = chess.turnNum;
    var inTurn;
    if (globalChess.inTurn == 1){ inTurn = "White"; }
    else {inTurn = "Black";}
    document.getElementById("inTurn").innerHTML = inTurn;
    var humanPlayerString;
    if (globalChess.humanPlayer == 1){ humanPlayerString = "White"; }
    else {humanPlayerString = "Black";}
    document.getElementById("humanPlayer").innerHTML = humanPlayerString;
    document.getElementById("status").innerHTML = "Game in progress";
}

// Tranlates boardtype used in serverside python script, to client side board (TODO: Should be done serverside?)
function pythonToJsBoard(pythonBoard){
    var jsBoard = [...Array(8)].map(e => Array(8));
    for (var r = 0; r < 8; r++) {
        for (var c = 0; c < 8; c++) {
            var pyPiece = pythonBoard[r][c];
            if (pyPiece == 0){ continue; }
            var type;
            switch (Math.abs(pythonBoard[r][c])){
                case 1:
                    type = "P";
                    break;
                case 2:
                    type = "R"
                    break;
                case 3:
                    type = "N";
                    break;
                case 4:
                    type = "B";
                    break;
                case 10:
                    type = "Q";
                    break;
                case 100:
                    type = "K";
                    break;
                default:
                    console.log("Unknown type. This shouldn't happen");
            }
            var team;
            if (pyPiece > 0) { team = 1; }
            else { team = -1; }
            jsBoard[r][c] = new Piece(type, team, r, c);
        }
    }
    return jsBoard;
}

$(document).ready(() => {
    const protocol = document.location.protocol.startsWith('https') ? 'wss://' : 'ws://';
    webSocket = new WebSocket(protocol + location.host);
    console.log("Websocket created with args: " + protocol + location.host);

    document.getElementById("3rdButton").addEventListener("click", () => {
        webSocket.send("Stuff");
        console.log("Sent stuff to server");
    });

    document.getElementById("loadGameButton").addEventListener("click", () => {
        console.log("TODO: Fix load button");
        var gameID = prompt("Game ID");
        var message = {action: "load game",
                       id: gameID};
        webSocket.send(JSON.stringify(message));
    });

    document.getElementById("newGameButton").addEventListener("click", () => {

        var newID = (Math.random().toString(36)+'00000000000000000').slice(2, 10);
        newID = prompt("Choose Instance ID", newID);

        if (newID == null){ // If cancelled prompt
            return;
        }

        var message = {action: "new game",
                       id: newID,
                       humanPlayer: 1}; //TODO: Fix for human playing as black
        console.log(newID);
        webSocket.send(JSON.stringify(message));
    });

    document.getElementById("promoteRookButton").addEventListener("click", () => {
        document.getElementById("promoteBox").style.display = 'none';
        promotionMove(2);
    });

    document.getElementById("promoteKnightButton").addEventListener("click", () => {
        document.getElementById("promoteBox").style.display = 'none';
        promotionMove(3);
    });

    document.getElementById("promoteBishopButton").addEventListener("click", () => {
        document.getElementById("promoteBox").style.display = 'none';
        promotionMove(4);
    });

    document.getElementById("promoteQueenButton").addEventListener("click", () => {
        document.getElementById("promoteBox").style.display = 'none';
        promotionMove(10);
    });

    webSocket.onmessage = (event) => {
        console.log("socket message received ", JSON.parse(event.data));
        var response = JSON.parse(event.data);
        var status = Number(response.status);
        switch (status) {
            case 200:
                console.log("Player move success"); // TODO (?) validate game state
                finishMove(response.move);
    
                // Asking for ai move
                var message = {action: "ai move",
                               id: id};
                webSocket.send(JSON.stringify(message));
                break;
            case 201:
                console.log("New game succesfully started (on server)");
                if (globalChess != null){
                    deleteHtmlPieces(globalChess);
                }
                beginNewGame(response.id, response.humanPlayer);
                break;
            case 202:
                console.log("TODO GAME LOAD");
                // gameID, pyBoard, turn, humanPlayer, in_turn
                loadGame(response.id, response.board, response.turn, response.humanPlayer, response.inTurn);
                if (response.inTurn != response.humanPlayer) {
                    var message = {action: "ai move",
                                   id: id};
                    webSocket.send(JSON.stringify(message));
                }
                break;
            case 203:
                console.log("Player move success. Game ended");
                var msg = "Game over. Winner: ";
                if (response.winner == 1) {msg += "White"}
                else if (response.winner == -1) {msg += "Black"}
                else {msg = "Game over. Draw"}
                finishMove(response.move);
                alert(msg);
                document.getElementById("status").innerHTML = msg;
                waiting = true;
                break;
            case 210:
                console.log("Recieved ai move from server");
                finishMove(response.move);
                // waiting = false;
                break;
            case 220:
                console.log("Needs promotion argument");
                var promoteBox = document.getElementById("promoteBox");
                promoteBox.style.zIndex = 10;
                promoteBox.style.display = "block";
                break;
            case 400:
                console.log("Illegal move. Status: " + response.status + ", with message: " + response.msg);
                waiting = false;
                break;
            case 500:
                console.log("Server error due to incompetent (or incomplete) programming. msg: " + response.msg);
                waiting = false;
                break;
            case 501:
                console.log("Generic server error. msg: " + response.msg);
                waiting = false;
                break;
            case 528:
                console.log("Game ID already in use");
                alert("Chosen Game ID is already in use");
                break;
            case 529:
                console.log("No such game to load");
                alert("No game with that ID to load");
                break;
            default:
                console.log("Unknown response code. Status: " + response.status + ", with message: " + response.msg);
                waiting = false;
        }
    }

    var canvas = document.getElementById("chess_canvas");
    drawChessBoard(canvas);
    var canvasRect = canvas.getBoundingClientRect();
    boardStartX = canvasRect.left + .5 * squareLength + .5 * lineWidth;
    boardStartY = canvasRect.top + .5 * squareLength + .5 * lineWidth;
    // console.log(boardStartX, boardStartY);

    canvas.addEventListener('click', boardEventHandler);
});


// TODO: let player play as black
// TODO: Refactor css 
// TODO: New game button deletes pieces before accept. If cancel option chosen, this may crash server (done)
// TODO: UI stuff for Id, Turn, ect. (Remember castling moves call move function twice) (done)
// TODO: reconsider 'waiting' variable
// TODO: Handle UI breaking down when scrolling/resizing
// TODO: Proper function documentation