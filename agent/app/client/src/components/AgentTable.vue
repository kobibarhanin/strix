<template>
        <div class="ui container" style="padding-bottom: 2%; ">
            <table id="jobs_table" class="ui selectable celled black table">
                <thead>
                <tr>
                <th>Role</th>
                <th>Job ID</th>
                <th>Repository</th>
                <th>Executable</th>
                <th>Update Time</th>
                <th>Status</th>
                </tr>
                </thead>
                <tbody v-cloak>
                    <tr v-for="job in jobs" :key="job.id">
                        <td>{{job.role}}</td>
                        <td>{{job.id}}</td>
                        <td>{{job.git_repo}}</td>
                        <td>{{job.file_name}}</td>
                        <td>{{job.update_time}}</td>
                        <td>{{job.job_status}}</td>
                    </tr>
                </tbody>
            </table>
        </div>
</template>

<script>
    export default {
        props: ['jobs'],
        name: "AgentTable"
    }
</script>

<style scoped>

</style>