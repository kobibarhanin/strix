<template>
    <div class="ui container" style="padding-bottom: 2%; ">
        <form class="ui form">
            <div class="ui fields">
                <h2 class="ui field header">Submit Job:</h2>
                <div class="ui six wide field">
                    <input type="text" v-model="git_repo" placeholder="Git URL">
                </div>
                <div class="ui six wide field">
                    <input type="text" v-model="file_name" placeholder="File name">
                </div>
                <button @click.prevent="submit" class="ui two wide field button" type="submit">Submit</button>
            </div>
        </form>
    </div>
</template>

<script>
    export default {
        name: "AgentForm",
        data: function() {
            return {
                git_repo: 'https://github.com/kobibarhanin/Strix.git\t',
                file_name: 'payloads/test_pipeline.groovy\t',
            }
        },
        methods: {
            submit: function() {
                this.$emit('submit', this.git_repo, this.file_name);
            }
        }
    }
</script>

<style scoped>

</style>