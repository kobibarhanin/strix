
document.getElementById("myButton").addEventListener("click", myFunction);
    function myFunction(){
       interact();
}

let {PythonShell} = require('python-shell')
var path = require("path")

function interact(){

    var python = require('python-shell')
    var path = require('path')

    var filepath = document.getElementById('in_filepath').value

    var options = {
        scriptPath: path.join(__dirname, ''),
        args: [filepath]
    }

    var result = new PythonShell('transmitter.py', options)

    result.on('message', function(message){
        swal(message)
    })

}