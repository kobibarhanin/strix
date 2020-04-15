jQuery.ajaxSettings.traditional = true;

role_colors = {
  "submit": "teal",
  "orchestrate": "blue",
  "execute": "purple"
};

status_colors = {
  "created": "yellow",
  "submitted": "orange",
  "completed": "green",
  "aborted": "red"
};

connectivity_colors = {
  "connected": "green",
  "disconnected": "red",
  "busy": "orange"
};

$(document).ready(function () {

    populate_jobs();
    setInterval(populate_jobs,5000);
    get_connectivity();
    setInterval(get_connectivity,5000);

    $("form#job_form").submit(function(e) {

        e.preventDefault();
        var formData = new FormData(this);
        console.log(formData);
        console.log(formData.get('git_repo'));
        console.log(formData.get('file_name'));

        $.get('/submit', { git_repo: formData.get('git_repo'), file_name: formData.get('file_name')},
            function(returnedData){
                 console.log(returnedData);
        });

    });

});


function get_connectivity(){
    $.getJSON('/connectivity',{},function(connectivity){
        $('#connectivity').html('<div class="ui '+connectivity_colors[connectivity['status']]+' big label">'+connectivity['status']+'</div>')
    });
}


function populate_jobs(){

    $.getJSON('/get_jobs',{},function(jobs){
        $('#tbodyid').empty();
        $.each(jobs, function(i, job) {
            $('#tbodyid').append(populate_job(jobs[i]))
        });

    });
}


function populate_job(job){
    let role_color = role_colors[job['role']];
    let status_color = status_colors[job['job_status']];
    let row_data = `
        <tr>
            <td>
                <a class="ui `+role_color+` label">`+job['role']+`</a>
            </td>
            <td>`+job['id']+`</td>
            <td>`+job['git_repo']+`</td>
            <td>`+job['file_name']+`</td>
            <td>`+job['update_time']+`</td>
            <td>
                <a href="/get_report?id=`+job['id']+`" id="`+job['id']+`"class="ui `+status_color+` label">`+job['job_status']+`</a>
            </td>
        </tr>
    `;
    return row_data
}

