<template>
    <div class="ui container" style="margin-top: 5%;">
        <img class="ui centered medium image" :src="image" />
        <h1 class="ui center aligned huge header" style="margin-bottom: 5%;">
            Agent - {{agent_name}}
            <div>
                <div class="ui green big label" style="margin-top:2%;">
                {{connectivity}}
                </div>
            </div>
        </h1>
    </div>
</template>

<script>
    import image from "../assets/logo.png"

    export default {
        name: "AgentHeader",
        props: ['agent_name', 'connectivity'],
        data: function () {
            return {
                image: image
            }
        }
    }
</script>

<style scoped>

</style>