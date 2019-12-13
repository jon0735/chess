var spawn = require('child_process').spawn;

var process = spawn('python',["./pythonstuff.py", 
    2, 
    3]); 

process.stdout.on('data', (data) => {
    console.log("On Data");
    console.log(data.toString());
});

// setTimeout( () => {
//     console.log('meh')}, 6000);