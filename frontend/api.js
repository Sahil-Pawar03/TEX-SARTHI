// TEX-SARTHI Frontend API Integration
// This script provides a complete interface to the backend API

class TexSarthiAPI {
  constructor() {
    this.baseURL = window.location.protocol === 'file:' ? 'http://localhost:3000/api' : '/api';
    this.token = localStorage.getItem('auth_token');
  }

  // Set authentication token
  setToken(token) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  // Clear authentication token
  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  // Make authenticated API request
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { 'Authorization': `Bearer ${this.token}` })
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      
      if (response.status === 401) {
        this.clearToken();
        window.location.href = 'login.html';
        return;
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Request failed' }));
        throw new Error(error.error || 'Request failed');
      }

      return await response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  // Authentication methods
  async login(email, password) {
    const response = await this.request('/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    this.setToken(response.token);
    return response;
  }

  async signup(name, email, password) {
    const response = await this.request('/signup', {
      method: 'POST',
      body: JSON.stringify({ name, email, password })
    });
    this.setToken(response.token);
    return response;
  }

  logout() {
    this.clearToken();
  }

  // Dashboard methods
  async getDashboardStats() {
    return await this.request('/dashboard/stats');
  }

  // Orders methods
  async getOrders(filters = {}) {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);
    
    const queryString = params.toString();
    return await this.request(`/orders${queryString ? `?${queryString}` : ''}`);
  }

  async createOrder(orderData) {
    return await this.request('/orders', {
      method: 'POST',
      body: JSON.stringify(orderData)
    });
  }

  async updateOrder(id, orderData) {
    return await this.request(`/orders/${id}`, {
      method: 'PUT',
      body: JSON.stringify(orderData)
    });
  }

  async deleteOrder(id) {
    return await this.request(`/orders/${id}`, {
      method: 'DELETE'
    });
  }

  // Customers methods
  async getCustomers(search = '') {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    
    const queryString = params.toString();
    return await this.request(`/customers${queryString ? `?${queryString}` : ''}`);
  }

  async createCustomer(customerData) {
    return await this.request('/customers', {
      method: 'POST',
      body: JSON.stringify(customerData)
    });
  }

  async updateCustomer(id, customerData) {
    return await this.request(`/customers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(customerData)
    });
  }

  // Inventory methods
  async getInventory(filters = {}) {
    const params = new URLSearchParams();
    if (filters.type) params.append('type', filters.type);
    if (filters.search) params.append('search', filters.search);
    
    const queryString = params.toString();
    return await this.request(`/inventory${queryString ? `?${queryString}` : ''}`);
  }

  async createInventoryItem(itemData) {
    return await this.request('/inventory', {
      method: 'POST',
      body: JSON.stringify(itemData)
    });
  }

  async updateInventoryItem(id, itemData) {
    return await this.request(`/inventory/${id}`, {
      method: 'PUT',
      body: JSON.stringify(itemData)
    });
  }

  // Invoices methods
  async getInvoices(filters = {}) {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);
    
    const queryString = params.toString();
    return await this.request(`/invoices${queryString ? `?${queryString}` : ''}`);
  }

  async createInvoice(invoiceData) {
    return await this.request('/invoices', {
      method: 'POST',
      body: JSON.stringify(invoiceData)
    });
  }

  // Deliveries methods
  async getDeliveries(filters = {}) {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);
    
    const queryString = params.toString();
    return await this.request(`/deliveries${queryString ? `?${queryString}` : ''}`);
  }

  async createDelivery(deliveryData) {
    return await this.request('/deliveries', {
      method: 'POST',
      body: JSON.stringify(deliveryData)
    });
  }

  // Reports methods
  async getSalesReport(startDate, endDate) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const queryString = params.toString();
    return await this.request(`/reports/sales${queryString ? `?${queryString}` : ''}`);
  }

  // Settings methods
  async getSettings() {
    return await this.request('/settings');
  }

  async updateSettings(settingsData) {
    return await this.request('/settings', {
      method: 'PUT',
      body: JSON.stringify(settingsData)
    });
  }
}

// Create global API instance
window.api = new TexSarthiAPI();

// Enhanced auth.js integration
(function() {
  // Override the existing auth functions to use the API
  const originalHandleLoginSubmit = window.handleLoginSubmit;
  const originalHandleSignupSubmit = window.handleSignupSubmit;

  window.handleLoginSubmit = async function(e) {
    if (e && e.preventDefault) e.preventDefault();
    
    const emailInput = document.getElementById("email-input");
    const passInput = document.getElementById("password-input");
    const errorBox = document.getElementById("login-error");
    
    if (errorBox) errorBox.classList.add("hidden");

    const email = emailInput ? emailInput.value.trim() : "";
    const password = passInput ? passInput.value : "";

    if (!email || !password) {
      showLoginError("Please enter email and password.");
      return;
    }

    try {
      const response = await window.api.login(email, password);
      setSession(response.token, response.user.email, response.user.name);
      location.href = "index.html";
    } catch (error) {
      showLoginError(error.message || "Login failed. Please check your credentials and try again.");
    }
  };

  window.handleSignupSubmit = async function(e) {
    if (e && e.preventDefault) e.preventDefault();
    
    const nameInput = document.getElementById("name-input");
    const emailInput = document.getElementById("signup-email-input");
    const passInput = document.getElementById("signup-password-input");
    const errorBox = document.getElementById("signup-error");
    
    if (errorBox) errorBox.classList.add("hidden");

    const name = nameInput ? nameInput.value.trim() : "";
    const email = emailInput ? emailInput.value.trim() : "";
    const password = passInput ? passInput.value : "";

    if (!name || !email || !password) {
      showSignupError("Please fill in name, email and password.");
      return;
    }

    try {
      const response = await window.api.signup(name, email, password);
      setSession(response.token, response.user.email, response.user.name);
      location.href = "index.html";
    } catch (error) {
      showSignupError(error.message || "Signup failed. Please try again.");
    }
  };
})();

// Dashboard integration
document.addEventListener('DOMContentLoaded', async function() {
  // Load dashboard stats if on dashboard page
  if (window.location.pathname.includes('index.html')) {
    try {
      const stats = await window.api.getDashboardStats();
      
      // Update dashboard cards
      const totalOrdersEl = document.querySelector('.card.blue .card-value');
      const lowStockEl = document.querySelector('.card.red .card-value');
      const pendingDeliveriesEl = document.querySelector('.card.orange .card-value');
      const outstandingAmountEl = document.querySelector('.card.green .card-value');
      
      if (totalOrdersEl) totalOrdersEl.textContent = stats.totalOrders || 0;
      if (lowStockEl) lowStockEl.textContent = stats.lowStockItems || 0;
      if (pendingDeliveriesEl) pendingDeliveriesEl.textContent = stats.pendingDeliveries || 0;
      if (outstandingAmountEl) outstandingAmountEl.textContent = `₹${(stats.outstandingAmount || 0).toLocaleString()}`;
    } catch (error) {
      console.error('Failed to load dashboard stats:', error);
    }
  }

  // Load orders if on orders page
  if (window.location.pathname.includes('orders.html')) {
    try {
      const orders = await window.api.getOrders();
      const tbody = document.getElementById('orders-body');
      
      if (tbody && orders.length > 0) {
        tbody.innerHTML = '';
        
        orders.forEach(order => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${order.order_number}</td>
            <td>${order.customer_name || 'N/A'}</td>
            <td>${order.order_type}</td>
            <td>${order.fabric}</td>
            <td>${order.quantity}</td>
            <td>${order.delivery_date || 'N/A'}</td>
            <td>₹${order.order_value.toLocaleString()}</td>
            <td><span class="status ${getStatusClass(order.status)}">${order.status}</span></td>
            <td class="actions">
              <button class="btn elevated" onclick="viewOrder(${order.id})">View</button>
              <button class="btn elevated" onclick="editOrder(${order.id})">Edit</button>
            </td>
          `;
          tbody.appendChild(tr);
        });
      }
    } catch (error) {
      console.error('Failed to load orders:', error);
    }
  }

  // Load customers if on customers page
  if (window.location.pathname.includes('customers.html')) {
    try {
      const customers = await window.api.getCustomers();
      const container = document.querySelector('.customer-cards');
      
      if (container && customers.length > 0) {
        container.innerHTML = '';
        
        customers.forEach(customer => {
          const card = document.createElement('div');
          card.className = 'customer-card';
          card.innerHTML = `
            <h3>${customer.name}</h3>
            <p>${customer.phone || 'N/A'} • ${customer.email || 'N/A'}</p>
            <p>${customer.address || 'N/A'}</p>
            <p><strong>Total Orders:</strong> ${customer.total_orders} • <strong>Total Spent:</strong> ₹${customer.total_spent.toLocaleString()}</p>
            <p><strong>Outstanding:</strong> ₹${customer.outstanding_amount.toLocaleString()} • <strong>Last Order:</strong> ${customer.last_order_date || 'N/A'}</p>
            <button class="btn elevated" onclick="viewCustomerOrders(${customer.id})">View Orders</button>
          `;
          container.appendChild(card);
        });
      }
    } catch (error) {
      console.error('Failed to load customers:', error);
    }
  }

  // Load inventory if on inventory page
  if (window.location.pathname.includes('inventory.html')) {
    try {
      const inventory = await window.api.getInventory();
      const tbody = document.querySelector('#inventory-table tbody');
      
      if (tbody && inventory.length > 0) {
        tbody.innerHTML = '';
        
        inventory.forEach(item => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${item.item_name}</td>
            <td>${item.type}</td>
            <td>${item.color || 'N/A'}</td>
            <td>${item.current_stock}</td>
            <td>${item.min_stock}</td>
            <td>₹${item.cost_per_unit}</td>
            <td>₹${item.total_value.toLocaleString()}</td>
            <td>${item.supplier || 'N/A'}</td>
            <td><span class="status ${getStatusClass(item.status)}">${item.status}</span></td>
            <td>
              <button class="btn elevated" onclick="viewInventoryItem(${item.id})">View</button>
            </td>
          `;
          tbody.appendChild(tr);
        });
      }
    } catch (error) {
      console.error('Failed to load inventory:', error);
    }
  }
});

// Helper function to get status class
function getStatusClass(status) {
  const s = String(status || '').toLowerCase().trim();
  if (s === 'ready' || s === 'completed' || s === 'paid' || s === 'delivered' || s === 'in stock') return 'green';
  if (s === 'received' || s === 'partial') return 'blue';
  if (s.indexOf('progress') !== -1 || s === 'scheduled') return 'yellow';
  return 'red';
}

// Global functions for button actions
window.viewOrder = function(id) {
  console.log('View order:', id);
  // Implement view order functionality
};

window.editOrder = function(id) {
  console.log('Edit order:', id);
  // Implement edit order functionality
};

window.viewCustomerOrders = function(id) {
  console.log('View customer orders:', id);
  // Implement view customer orders functionality
};

window.viewInventoryItem = function(id) {
  console.log('View inventory item:', id);
  // Implement view inventory item functionality
};
