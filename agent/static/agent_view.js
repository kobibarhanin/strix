jQuery.ajaxSettings.traditional = true;


$(document).ready(function () {
    populate_jobs();
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
                    'agent': data['agent_assigned'],
                    'start': '-',
                    'end': '-',
                    'status': 'submitted'
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

function populate_jobs(){

    $.getJSON('/jobs',{},function(jobs){

        $.each(jobs, function(i, job) {
            job = jobs[i]
            entry = {
                'executable': job['payload'],
                'id': job['id'],
                'agent': job['assigned_agent'],
                'start': '-',
                'end': '-',
                'status': job['status']
            }
            add_to_row_table(entry,'jobs_table')
        });

    });
}


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
    cell6.innerHTML = entry['status']

}