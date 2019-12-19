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
        console.log(JSON.parse(data));
        console.log("move data received");
        let data_obj = JSON.parse(data);
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
    process.stdout.on('data', (data) => {
        let data_obj = JSON.parse(data);
        // TODO: Check data and call appropriate functions
        chess_obj = data_obj.chess;
    });
}



//TESTING
create('22');
setTimeout( () => {
    move(1, 3, 3, 3, chess_obj, '22');
}, 1000);
setTimeout( () => {
    move(6, 3, 4, 3, chess_obj, '22');
}, 2000);
setTimeout( () => {
    move(0, 4, 1, 3, chess_obj, '22');
}, 3000);
setTimeout( () => {
    console.log(chess_obj);
}, 4400);
