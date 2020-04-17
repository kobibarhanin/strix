<template>
  <div id="app">
    <AgentHeader
            :agent_name="agent_name"
            :connectivity="connectivity"
    />
    <AgentForm
            @submit="submit"
    />
    <AgentTable
            :jobs="jobs"
    />
  </div>
</template>

<script>

import AgentHeader from './components/AgentHeader.vue'
import AgentForm from './components/AgentForm.vue'
import AgentTable from './components/AgentTable.vue'

import axios from 'axios'

// var server_url = 'http://0.0.0.0:5000/';
var server_url = '/';

export default {
  name: 'App',
  components: {
    AgentHeader,
    AgentForm,
    AgentTable,
  },
  data() {
      return {
        jobs: [],
        connectivity: 'connected',
        agent_name: 'bitz_*',
      }
  },
  created: function() {
    this.get_jobs();
    setInterval(this.get_jobs,5000);
    this.get_connectivity();
    setInterval(this.get_connectivity,5000);
  },
  methods:{
    submit: function (git_repo, file_name){
      axios.get(server_url + 'submit', {
        params: {
            git_repo: git_repo.trim(),
            file_name: file_name.trim(),
        }
        });
    },
    get_jobs: function() {
      let _this = this;
      axios.get(server_url + 'get_jobs')
              .then(function (result) {
                _this.jobs = result.data
      });
    },
    get_connectivity: function() {
      let _this = this;
      axios.get(server_url + 'status')
              .then(function (status) {
                _this.connectivity = status.data.status;
                _this.agent_name = status.data.agent_name;
      });
    }
  }
}
</script>
