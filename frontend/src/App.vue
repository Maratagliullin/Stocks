<template>
  <div id="app">
    <div class="container-fluid">
      <div id="nav">
        <router-link to="/" exact>Главная</router-link>
         | 
        <router-link to="/ticker">Акции</router-link>
      </div>
      <router-view />
    </div>
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

#nav {
  padding: 30px 0px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: underline;
}

#nav a.router-link-active {
  color: #42b983;
}
</style>
