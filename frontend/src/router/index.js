import { createRouter, createWebHistory } from 'vue-router'
import ItemsView from '../views/ItemsView.vue'
import ExchangesView from '../views/ExchangesView.vue'

const routes = [
  { path: '/', redirect: '/items' },
  { path: '/items', name: 'Items', component: ItemsView },
  { path: '/exchanges', name: 'Exchanges', component: ExchangesView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
