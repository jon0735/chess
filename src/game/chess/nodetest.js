var spawn = require('child_process').spawn;

var chess_obj;

function move(rFrom, cFrom, rTo, cTo, chess, id) {
    var chessString = JSON.stringify(chess);
    var process = spawn('python', ["./chess_for_node.py",
        id,
        'move',
        rFrom,
        cFrom,
        rTo,
        cTo,
        chessString]);
    
    process.stdout.on('data', (data) => {
        console.log("STUFF")
        console.log(data.toString());
        console.log("STUFF2")
        console.log(JSON.parse(data));
        console.log("move data received");
        let data_obj = JSON.parse(data);
        console.log(data_obj.chess.legal_moves);
        let status = data_obj.status;
        // TODO: Properly handle returned data. Call appropriate functions.
        if (status == 200){
            console.log("MOVE SUCCESS");
            chess_obj = data_obj.chess;
        } else {
            console.log("MOVE FAILED");
        }
    });
}

function create(id){
    // TODO: Don't use child process. Giant overkill
    var process = spawn('python', ["./chess_for_node.py",
                        id,
                        'create']);
    console.log("created process created");
    process.stdout.on('data', (data) => {
        console.log("Create response");
        console.log(JSON.parse(data));
        console.log("MEH");
        let data_obj = JSON.parse(data);
        // TODO: Check data and call appropriate functions
        chess_obj = data_obj.chess;
    });
}

function aiMove(){
    var process = spawn('python', ["./chess_for_node.py",
                        '22',
                        'ai']); 
    process.stdout.on('data', (data) => {
        console.log("ai response");
        console.log(JSON.parse(data));
        console.log("ai MEH");
        let data_obj = JSON.parse(data);
        // TODO: Check data and call appropriate functions
        chess_obj = data_obj.chess;
    });  
}


//TESTING
create('22');
// console.log(chess_obj);
setTimeout( () => {
    move(1, 3, 3, 3, chess_obj, '22');
    console.log(chess_obj);
}, 3000);
setTimeout( () => {
    aiMove();
}, 6000);
// setTimeout( () => {
//     move(0, 4, 1, 3, chess_obj, '22');
// }, 3000);
// setTimeout( () => {
//     console.log(chess_obj);
// }, 4400);
