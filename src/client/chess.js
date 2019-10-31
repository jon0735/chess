const squareLength = 80; // MUST be 80 or integer stuff and images will break down
const lineWidth = 2;
var globalChess = null;
var selectedPiece = null;
var boardStartX;
var boardStartY;
var waiting = false;
var webSocket;
var moveInProgress;

class Chess {
    constructor(board, inTurn, humanPlayer){
        if (board === undefined){
            board = getStartBoard();
        }
        if (inTurn === undefined){
            inTurn = 1;
        }
        if (humanPlayer === undefined){
            humanPlayer = 1;
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
            console.log("Handle special move events (castle and that other one)");
        }
        var movedPiece = this.board[rFrom][cFrom];
        var htmlElement = movedPiece.htmlElement;
        htmlElement.style.outline = 'none';
        moveElementCell(this.board[rFrom][cFrom].htmlElement, rTo, cTo);
        var toPiece = this.board[rTo][cTo];
        if (toPiece != null && toPiece.htmlElement != null){
             toPiece.htmlElement.parentNode.removeChild(toPiece.htmlElement);
        }
        
        this.board[rFrom][cFrom] = null;
        movedPiece.row = rTo;
        movedPiece.column = cTo;
        this.board[rTo][cTo] = movedPiece;
        selectedPiece = null;
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
                pieceImg.style.position = "absolute";
                pieceImg.style.left = left + 0.5 * lineWidth + squareLength * (c + .5);
                pieceImg.style.top = top + 0.5 * lineWidth + squareLength * (7.5 - r);
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

// TODO MOVE PIECES
function enemyPieceEventHandler(event){
    if (waiting){
        console.log("Move in progress. Wait before doing more shit");
        return;
    }
    var htmlPiece = event.target;
    var piece = htmlPiece.piece;
    console.log("r = " + piece.row + ", c = " + piece.column);

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
    var piece = htmlPiece.piece;
    console.log("r = " + piece.row + ", c = " + piece.column);
    if (selectedPiece != null){
        selectedPiece.htmlElement.style.outline = 'none';
    }
    if (piece == selectedPiece) {
        selectedPiece = null;
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
    console.log("Event " + event.clientX + " : " + event.clientY);
    var rect = event.target.getBoundingClientRect();
    var x = event.clientX - rect.left; //x position within the element.
    var y = event.clientY - rect.top;  //y position within the element.
    console.log(x, y);
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
    // globalChess.move(rFrom, cFrom, rTo, cTo);
    // meh = rowColumnToChessNotation(r, c);
    // console.log(r, c);
    // console.log(meh[0], meh[1]);
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
    var message = {move: move,
                   validation: validation}
    webSocket.send(JSON.stringify(message));
}

function finishMove(){
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
    var toX = c * 80 + boardStartX; // + .5 * lineWidth;
    var toY = (7 - r) * 80 + boardStartY; // + .5 * lineWidth;
    moveElement(element, toX, toY);
}

function moveElement(element, toX, toY){

    // // console.log("start moveElement");
    // var startX = parseInt(element.style.left);
    // var startY = parseInt(element.style.top);
    // var currentX = startX;
    // var currentY = startY;
    // // console.log("toX: " + toX + ", startX = " + startX);
    // var xDist = toX - startX;
    // var yDist = toY - startY;
    // var dist = Math.sqrt(xDist * xDist + yDist * yDist)
    // // console.log("xdist = " + xDist + ", ydist = " + yDist + "dist = " + dist);
    // var xDirection = xDist / dist;
    // var yDirection = yDist / dist;
    // var max = Math.ceil(dist);
    // var count = 0;
    // // console.log("Just before interval");
    // var id = setInterval(frame, 1);
    // // console.log("Just after interval");
    // function frame(){
    //     // console.log("Start frame func");
    //     if (count >= max){
    //         // console.log("If");
    //         clearInterval(id);
    //     }
    //     else {
    //         // console.log("Else, currentX= " + parseInt(currentX) + ", currentY = " + parseInt(currentY));
    //         count++;
    //         currentX += xDirection;
    //         currentY += yDirection;
    //         element.style.left = parseInt(currentX);
    //         element.style.top = parseInt(currentY);
    //     }
    //     // clearInterval(id);
    //     // console.log("end frame func");
    // }

    element.style.top = toY;
    element.style.left = toX;
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


$(document).ready(() => {
    const protocol = document.location.protocol.startsWith('https') ? 'wss://' : 'ws://';
    webSocket = new WebSocket(protocol + location.host);
    console.log("Websocket created with args: " + protocol + location.host);

    document.getElementById("3rdButton").addEventListener("click", () => {
        webSocket.send("Stuff");
        console.log("Sent stuff to server");
    });

    document.getElementById("loadGameButton").addEventListener("click", () => {
        deleteHtmlPieces(globalChess);
    });

    document.getElementById("newGameButton").addEventListener("click", () => {
        if (globalChess != null){
            deleteHtmlPieces(globalChess);
        }
        var chess = new Chess();
        drawHtmlPieces(chess);
        globalChess = chess;
    });

    webSocket.onmessage = (event) => {
        console.log("socket message received ", JSON.parse(event.data));
        var respone = JSON.parse(event.data);
        if(respone.status == "done"){
            console.log("success");
            finishMove();
        } else{
            console.log("TODO: handle incorrect move correctly");
            moveElementCell = Null;
            waiting = false;
        }
    }

    var canvas = document.getElementById("chess_canvas");
    drawChessBoard(canvas);
    var canvasRect = canvas.getBoundingClientRect();
    boardStartX = canvasRect.left + .5 * squareLength + .5 * lineWidth;
    boardStartY = canvasRect.top + .5 * squareLength + .5 * lineWidth;
    console.log(boardStartX, boardStartY);

    canvas.addEventListener('click', boardEventHandler);
});
