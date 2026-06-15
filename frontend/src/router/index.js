import { createRouter, createWebHistory } from 'vue-router'
import ItemsView from '../views/ItemsView.vue'
import ExchangesView from '../views/ExchangesView.vue'
import MarketPricesView from '../views/MarketPricesView.vue'
import DashboardView from '../views/DashboardView.vue'
import RecycleBinView from '../views/RecycleBinView.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: DashboardView },
  { path: '/items', name: 'Items', component: ItemsView },
  { path: '/exchanges', name: 'Exchanges', component: ExchangesView },
  { path: '/market', name: 'Market', component: MarketPricesView },
  { path: '/recycle', name: 'Recycle', component: RecycleBinView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
