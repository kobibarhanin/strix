jQuery.ajaxSettings.traditional = true;
$(document).ready(function () {
//    populate_jobs();
         $("form#job_form").submit(function(e) {
            e.preventDefault();
            var formData = new FormData(this);

            $.ajax({
                url: '/execute',
                type: 'POST',
                data: formData,
                success: function (data) {
                    entry = {
                        'executable': data['payload'],
                        'id': data['id'],
                        'agent': data['agent'],
                        'start': '-',
                        'end': '-',
                    }
                    add_to_row_table(entry,'jobs_table')
                },
                cache: false,
                contentType: false,
                processData: false
            });
        });
//    setTimeout(function(){
//        window.location.reload(1);
//    }, 5000);
});



//function populate_agents(){
//    $.getJSON("/agents",{},function(agents){
//        $.each(agents, function(index, agent){
//            let id = Math.random().toString(36).substring(7);
//            console.log('agent status: ' + agent['status'])
//            if (agent['status']=='ready'){
//                status = 'Ready';
//                classColor = 'green';
//            }
//            else if (agent['status']=='disconnected'){
//                status = 'Disconnected';
//                classColor = 'red';
//            } else if (agent['status']=='busy') {
//                status = 'Busy';
//                classColor = 'orange';
//            }
//            $('#agents_view_table').append('<tr><td>'+agent['name']+'</td><<td>'+agent['port']+'</td><td>'+agent['timestamp']+'</td><td><div class="ui '+classColor+' label">'+status+'</div></td></tr>');
//        });
//    });
//}

function add_to_row_table(entry,table_id) {
    var table = document.getElementById(table_id).getElementsByTagName('tbody')[0];
    var row = table.insertRow(table.rows.length);
    row.id = "row_"+entry["id"];
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var cell3 = row.insertCell(2);
    var cell4 = row.insertCell(3);
    var cell5 = row.insertCell(4);
    var cell6 = row.insertCell(5);
    cell1.innerHTML = entry['executable'];
    cell2.innerHTML = entry['id'];
    cell3.innerHTML = entry["agent"];
    cell4.innerHTML = entry["start"];
    cell5.innerHTML = entry["end"];
    cell6.innerHTML = "submitted"

}