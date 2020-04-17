<template>
        <div class="ui container" style="padding-bottom: 2%; ">
            <table id="jobs_table" class="ui selectable celled black table">
                <thead>
                <tr>
                <th style="width: 12%;">Role</th>
                <th>Job ID</th>
                <th>Repository</th>
                <th>Executable</th>
                <th>Update Time</th>
                <th style="width: 12%;">Status</th>
                </tr>
                </thead>
                <tbody v-cloak>
                    <tr v-for="job in jobs" :key="job.id">
                        <td>
                        <i v-bind:class="role_class(job.role)"></i>
                            {{job.role}}
                        </td>
                        <td>{{job.id}}</td>
                        <td>{{job.git_repo}}</td>
                        <td>{{job.file_name}}</td>
                        <td>{{job.update_time}}</td>
                        <td>
                            <div v-bind:class="status_class(job.job_status)">
                                {{job.job_status}}
                                <a v-if="job.job_status === 'completed'"
                                   :href="'/get_report?id='+job.id" download>
                                    <i class="ui download icon"></i>
                                </a>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
</template>

<script>
    export default {
        props: ['jobs'],
        name: "AgentTable",
        data: function() {
          return {
            status_colors: {
                "created": "yellow",
                "submitted": "orange",
                "completed": "green",
                "aborted": "red"
            },
            role_icons: {
                "submit": "code",
                "orchestrate": "sitemap",
                "execute": "terminal"
            },
          }
        },
        methods: {
            status_class: function(status) {
                return [this.status_colors[status], "ui", "label"]
            },
            role_class: function(role) {
                return [this.role_icons[role], "ui", "icon"]
            }
        }
    }
</script>

<style scoped>

</style>