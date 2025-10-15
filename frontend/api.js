// TEX-SARTHI Frontend API Integration
// This script provides a complete interface to the backend API

class TexSarthiAPI {
  constructor() {
    // Always call the Flask backend running on port 3000
    // The static server on 8080 does not proxy /api paths
    this.baseURL = 'http://localhost:3000/api';
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
        console.warn('Authentication failed, clearing token');
        this.clearToken();
        // Try to auto-login with default credentials
        if (endpoint !== '/login') {
          try {
            await this.login('admin@texsarthi.com', 'admin123');
            // Retry the original request
            const retryConfig = {
              ...config,
              headers: {
                ...config.headers,
                'Authorization': `Bearer ${this.token}`
              }
            };
            const retryResponse = await fetch(url, retryConfig);
            if (retryResponse.ok) {
              return await retryResponse.json();
            }
          } catch (loginError) {
            console.error('Auto-login failed:', loginError);
          }
        }
        throw new Error('Authentication required');
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: `HTTP ${response.status}: ${response.statusText}` }));
        throw new Error(error.error || `Request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
        console.error('Network error - is the backend running?');
        throw new Error('Unable to connect to server. Please check if the backend is running on port 3000.');
      }
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
    const res = await this.request(`/orders${queryString ? `?${queryString}` : ''}`);
    return res && res.orders ? res.orders : [];
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
    const res = await this.request(`/customers${queryString ? `?${queryString}` : ''}`);
    return res && res.customers ? res.customers : [];
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
    const res = await this.request(`/inventory${queryString ? `?${queryString}` : ''}`);
    return res && res.inventory ? res.inventory : [];
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

  // AI Invoice methods
  async checkAIAvailability() {
    return await this.request('/invoices/ai-available');
  }

  async getAIInvoiceSuggestions(orderId) {
    return await this.request(`/ai/invoices/suggestions/${orderId}`);
  }

  async generateAIInvoice(orderId, options = {}) {
    return await this.request(`/ai/invoices/generate/${orderId}`, {
      method: 'POST',
      body: JSON.stringify(options)
    });
  }

  async analyzeOrderForInvoice(orderId) {
    return await this.request(`/ai/invoices/analyze-order/${orderId}`);
  }

  async bulkGenerateAIInvoices(orderIds, options = {}) {
    return await this.request('/ai/invoices/bulk-generate', {
      method: 'POST',
      body: JSON.stringify({ order_ids: orderIds, ...options })
    });
  }

  async getInvoiceTemplates() {
    return await this.request('/ai/invoices/templates');
  }

  async calculateSmartPricing(items) {
    return await this.request('/ai/invoices/smart-pricing', {
      method: 'POST',
      body: JSON.stringify({ items })
    });
  }

  async getAIInvoiceStats() {
    return await this.request('/ai/invoices/stats');
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
              <button class="btn primary" onclick="createInvoice(${order.id})">Create Invoice</button>
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
  (async () => {
    try {
      const data = await window.api.request(`/orders/${id}`);
      const o = data.order || {};
      alert(`Order Details\n\n# ${o.order_number}\nCustomer: ${o.customer_name || 'N/A'}\nType: ${o.order_type}\nFabric: ${o.fabric || 'N/A'}\nQuantity: ${o.quantity}\nDelivery: ${o.delivery_date || 'N/A'}\nValue: ₹${(o.order_value||0).toLocaleString()}\nStatus: ${o.status}`);
    } catch (err) {
      alert(`Failed to load order: ${err.message || err}`);
    }
  })();
};

window.editOrder = function(id) {
  (async () => {
    try {
      const current = await window.api.request(`/orders/${id}`);
      const o = current.order || {};
      const qty = prompt('Update quantity', String(o.quantity ?? ''));
      if (qty === null) return;
      const status = prompt('Update status (pending, in_progress, completed, cancelled)', String(o.status ?? 'pending'));
      if (status === null) return;
      await window.api.updateOrder(id, { quantity: Number(qty), status });
      alert('Order updated');
      location.reload();
    } catch (err) {
      alert(`Failed to update order: ${err.message || err}`);
    }
  })();
};

window.viewCustomerOrders = function(id) {
  console.log('View customer orders:', id);
  // Implement view customer orders functionality
};

window.viewInventoryItem = function(id) {
  console.log('View inventory item:', id);
  // Implement view inventory item functionality
};

// "AI" helper to propose invoice details and create it
window.createInvoice = function(orderId) {
  (async () => {
    try {
      // Fetch the order to base our suggestions on
      const resp = await window.api.request(`/orders/${orderId}`);
      const o = resp.order || {};
      const baseAmount = Math.max(0, Number(o.order_value || 0) - Number(o.advance_payment || 0));
      const suggestedTaxRate = 0.18; // 18% GST default
      const today = new Date();
      const suggestedDue = new Date(today.getFullYear(), today.getMonth(), today.getDate() + 7);

      // AI-style suggestion text for user context
      const summary = [
        `Customer: ${o.customer_name || 'N/A'}`,
        `Order: ${o.order_number || ''} (${o.order_type || ''})`,
        `Net amount (order - advance): ₹${baseAmount.toLocaleString()}`,
        `Suggested tax: ${(suggestedTaxRate * 100).toFixed(0)}%`,
        `Suggested due date: ${suggestedDue.toISOString().slice(0,10)}`
      ].join('\n');

      // Confirm with user, allow edits via prompts
      alert(`Invoice Assistant Suggestions\n\n${summary}`);
      const amountStr = prompt('Invoice amount (before tax)', String(baseAmount));
      if (amountStr === null) return;
      const taxRateStr = prompt('Tax rate (e.g. 0.18 for 18%)', String(suggestedTaxRate));
      if (taxRateStr === null) return;
      const dueStr = prompt('Due date (YYYY-MM-DD)', suggestedDue.toISOString().slice(0,10));
      if (dueStr === null) return;
      const notes = prompt('Notes (optional)', `Auto-generated for ${o.order_number}`) || '';

      const payload = {
        amount: Number(amountStr),
        tax_rate: Number(taxRateStr),
        due_date: dueStr,
        notes
      };

      const created = await window.api.request(`/orders/${orderId}/invoice`, {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      const inv = created && created.invoice ? created.invoice : {};
      alert(`Invoice created: ${inv.invoice_number || ''}\nTotal: ₹${(inv.total_amount||0).toLocaleString()}`);
    } catch (err) {
      alert(`Failed to create invoice: ${err.message || err}`);
    }
  })();
};
