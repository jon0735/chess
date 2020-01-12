// import { json } from "body-parser";

const squareLength = 80; // MUST be 80 or integer stuff and images will break down. TODO: fix
const lineWidth = 2;
var globalChess = null;
var selectedPiece = null;
var id = null;
var boardStartX;
var boardStartY;
var waiting = false;
var webSocket;
var moveInProgress;

class Chess {
    constructor(humanPlayer, board, inTurn){
        if (board === undefined){
            board = getStartBoard();
        }
        if (humanPlayer === undefined){
            humanPlayer = 1;
        }
        if (inTurn === undefined){
            inTurn = 1;
        }
        this.board = board;
        this.inTurn = inTurn;
        this.humanPlayer = humanPlayer;
    }

    move(rFrom, cFrom, rTo, cTo, special){
        if(this.board[rFrom][cFrom] == null){
            console.log("Attempted move on non existant piece")
            return;
        }
        if (!(special == undefined || special == null)){
            console.log("TODO Handle special move events (castle and that other one)");
        }
        var movedPiece = this.board[rFrom][cFrom];
        var htmlElement = movedPiece.htmlElement;
        htmlElement.style.outline = 'none';
        // moveElementCell(this.board[rFrom][cFrom].htmlElement, rTo, cTo);
        var toPiece = this.board[rTo][cTo];
        if (toPiece != null && toPiece.htmlElement != null){
             toPiece.htmlElement.parentNode.removeChild(toPiece.htmlElement);
        }
        
        this.board[rFrom][cFrom] = null;
        movedPiece.row = rTo;
        movedPiece.column = cTo;
        this.board[rTo][cTo] = movedPiece;
        selectedPiece = null;
        moveElementCell(htmlElement, rTo, cTo);

    }
}

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

function deleteHtmlPieces(chess){
    console.log("Delete pieces called");
    if (chess == null){
        console.log("Chess is null");
        return;
    }
    var board = chess.board;
    // console.log("Before loop");
    for (var r = 0; r < 8; r++){
        for (var c = 0; c < 8; c++){
            // console.log("r = " + r + ", c = " + c);
            var piece = board[r][c];
            if (piece == null){
                console.log("Piece is null. Continuing");
                continue;
            }
            var htmlElement = piece.htmlElement;
            if (htmlElement == null){
                console.log("Html element is null. Continuing");
                continue;
            }
            htmlElement.parentNode.removeChild(htmlElement);
            piece.htmlElement = null;
        }
    }
}

function drawHtmlPieces(chess){ // should always call deleteHtmlPieces before
    console.log("draw called");
    var board = chess.board;
    var offset = document.getElementById("board_div").getBoundingClientRect();
    var top = offset.top;
    var left = offset.left;
    // console.log("before loop");
    for (var r = 0; r < 8; r++){
        for (var c = 0; c < 8; c++){
            // console.log("loop: " + r + ", " + c);
            var piece = board[r][c];
            // console.log("stuff " + piece);
            if (piece == null){
                continue;
            }
            var htmlElement = piece.htmlElement;
            if (htmlElement == null){
                // console.log("Start html null");
                // console.log(getPieceImageName(piece));
                var pieceImg = document.createElement('img');
                pieceImg.src = "resources/" + getPieceImageName(piece);
                pieceImg.style.transitionTimingFunction = "linear";
                pieceImg.style.zIndex = 1;
                pieceImg.style.position = "absolute";
                pieceImg.style.left = Math.round(left + 0.5 * lineWidth + squareLength * (c + .5));
                pieceImg.style.top = Math.round(top + 0.5 * lineWidth + squareLength * (7.5 - r));
                document.getElementById("chess_div_right").appendChild(pieceImg);
                piece.htmlElement = pieceImg;
                // console.log("End html null");
            } else{
                console.log("Existing Piece found while drawing. Someone fucked up");
            }
            if (piece.team == chess.humanPlayer){
                piece.htmlElement.addEventListener('click', ownPieceEventHandler);
            } else {
                piece.htmlElement.addEventListener('click', enemyPieceEventHandler);
            }
            piece.htmlElement.piece = piece;
        }
    }
}

function enemyPieceEventHandler(event){
    if (waiting){
        console.log("Move in progress. Wait before doing more shit");
        return;
    }
    var htmlPiece = event.target;
    var piece = htmlPiece.piece;
    // console.log("r = " + piece.row + ", c = " + piece.column);

    if (selectedPiece != null){
        console.log("Attempt move");
        attemptMove(selectedPiece.row, selectedPiece.column, piece.row, piece.column);
        // moveElement(htmlPiece, 200, 200);
    }
}

function ownPieceEventHandler(event){
    if (waiting){
        console.log("Move in progress. Wait before doing more shit");
        return;
    }
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
}

function boardEventHandler(event){
    if (waiting){
        console.log("Move in progress. Wait before doing more shit");
        return;
    }
    // console.log("Event " + event.clientX + " : " + event.clientY);
    var rect = event.target.getBoundingClientRect();
    var x = event.clientX - rect.left; //x position within the element.
    var y = event.clientY - rect.top;  //y position within the element.
    // console.log(x, y);
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
    attemptMove(rFrom, cFrom, rTo, cTo);
}

function rowColumnToChessNotation(row, column){
    var letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    return [letters[column], row + 1];
}

function attemptMove(rFrom, cFrom, rTo, cTo, special){
    waiting = true;
    if (special == undefined){
        special = null;
    }
    var move = {rFrom: rFrom,
                cFrom: cFrom,
                rTo: rTo,
                cTo: cTo,
                special: special};
    moveInProgress = move;
    var boardString = boardToString(globalChess.board);
    // console.log(boardString);
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

function finishMove(){
    console.log("Finish move called")
    globalChess.move(moveInProgress.rFrom, moveInProgress.cFrom, moveInProgress.rTo, moveInProgress.cTo, moveInProgress.special);
    waiting = false;
    console.log("TODO: finish move stuff");
}

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

function getPieceImageName(piece){
    var type = piece.type;
    var team = piece.team;
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

function moveElementCell(element, r, c){
    console.log("MoveElementCell called", r, c);
    var toX = Math.round(c * 80 + boardStartX);
    var toY = Math.floor((7 - r) * 80 + boardStartY);
    console.log("X: ", c * 80 + boardStartX);
    console.log("Y: ", (7 - r) * 80 + boardStartY);
    moveElement(element, toX, toY);
}

function moveElement(element, toX, toY){
    // console.log("MoveElement called", toX, toY);
    var startX = parseInt(element.style.left);
    var startY = parseInt(element.style.top);
    var xDist = toX - startX;
    var yDist = toY - startY;
    var dist = Math.sqrt(xDist * xDist + yDist * yDist)
    var animationTime = Math.floor(dist/.8);
    // console.log(dist/800)
    element.style.transitionTimingFunction = "linear";
    element.style.transitionDuration = "" + animationTime + "ms"; // dist/800 -> 0.1s per square (80px) ish
    element.style.top = toY;
    element.style.left = toX;
    setTimeout(() =>{
        element.style.zIndex = 1;
        element.style.transitionDuration = "0s";
    }, animationTime);
}

/**
 * Draws chess board. Numbering and all.
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

function beginNewGame(newId, humanPlayer){
    id = newId;
    var chess = new Chess(humanPlayer);
    drawHtmlPieces(chess);
    globalChess = chess;
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
        deleteHtmlPieces(globalChess);
    });

    document.getElementById("newGameButton").addEventListener("click", () => {
        if (globalChess != null){
            deleteHtmlPieces(globalChess);
        }
        var newID = (Math.random().toString(36)+'00000000000000000').slice(2, 10);
        newID = prompt("Choose Instance ID", newID);
        var message = {action: "new game",
                       id: newID,
                       humanPlayer: 1}; //TODO: Fix for humna playing as black
        webSocket.send(JSON.stringify(message));
        // var stuff = confirm("stuff");
        // var chess = new Chess();
        // drawHtmlPieces(chess);
        // globalChess = chess;
    });

    webSocket.onmessage = (event) => {
        console.log("socket message received ", JSON.parse(event.data));
        var response = JSON.parse(event.data);
        if(response.status == 200){ // Not a secure way of handling a successful move
            console.log("TODO: check stuff when move is success (ID and stuff)");
            console.log("success");
            finishMove();
            // Asking for ai move
            var message = {action: "ai move",
                           id: id};
            webSocket.send(JSON.stringify(message));
        } else if (response.status == 201){
            beginNewGame(response.id, response.humanPlayer);
        } else if (response.status == 210) {
            console.log("Recieved ai move from server");
            //TODO ai move stuff
        } else{
            console.log("TODO: handle incorrect move correctly. Status: " + response.status);
            // moveElementCell = null;
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