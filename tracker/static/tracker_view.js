jQuery.ajaxSettings.traditional = true;
$(document).ready(function () {
    populate_agents();
    setInterval(populate_agents,5000);
    get_logs();
    setInterval(get_logs,5000);
});

function populate_agents(){
    $.getJSON("/agents",{},function(agents){
        $("#agents_view_body").empty();
        $.each(agents, function(index, agent){
            let id = Math.random().toString(36).substring(7);
            console.log('agent status: ' + agent['status'])
            if (agent['status']=='connected'){
                status = 'connected';
                classColor = 'green';
            }
            else if (agent['status']=='disconnected'){
                status = 'Disconnected';
                classColor = 'red';
            } else {
                status = agent['status'];
                classColor = 'orange';
            }
            $('#agents_view_table').append('<tr><td>'+agent['name']+'</td><<td>'+agent['port']+'</td><td>'+agent['timestamp']+'</td><td><div class="ui '+classColor+' label">'+status+'</div></td></tr>');
        });
    });
}

function get_logs(){
    $.getJSON('/log_export',{},function(logs){
        $('#log_flow').html(logs)
    });
}
