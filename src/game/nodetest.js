var spawn = require('child_process').spawn;

var process = spawn('python',["./chess_for_node.py", 
    'create', 
    22]); 

process.stdout.on('data', (data) => {
    console.log("On Data");
    console.log(data.toString());
});