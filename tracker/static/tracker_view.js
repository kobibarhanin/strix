jQuery.ajaxSettings.traditional = true;
$(document).ready(function () {
    populate_agents();
    setTimeout(function(){
        window.location.reload(1);
    }, 5000);
});

function populate_agents(){
    $.getJSON("/agents",{},function(agents){
        $.each(agents, function(index, agent){
            let id = Math.random().toString(36).substring(7);
            console.log('agent status: ' + agent['status'])
            if (agent['status']=='ready'){
                status = 'Ready';
                classColor = 'green';
            }
            else if (agent['status']=='disconnected'){
                status = 'Disconnected';
                classColor = 'red';
            } else if (agent['status']=='busy') {
                status = 'Busy';
                classColor = 'orange';
            }
            $('#agents_view_table').append('<tr><td>'+agent['name']+'</td><<td>'+agent['port']+'</td><td>'+agent['timestamp']+'</td><td><div class="ui '+classColor+' label">'+status+'</div></td></tr>');
        });
    });
}
