/**
 * TODOIT Web Interface - New Hierarchical Architecture
 * Two-level view: Lists → List Details with Items
 */

class TodoAppNew {
    constructor() {
        this.currentView = 'lists';
        this.currentListKey = null;
        this.listsTable = null;
        this.itemsTable = null;
        this.currentPage = 0;
        this.pageSize = 20;
        this.searchTerm = '';
        this.showFavoritesOnly = false;
        
        this.init();
    }

    async init() {
        console.log('TodoApp initializing...'); // Debug log
        this.setupEventListeners();
        await this.showListsView();
        this.hideLoading();
        console.log('TodoApp initialized successfully'); // Debug log
    }

    setupEventListeners() {
        // Navigation
        document.getElementById('back-to-lists').addEventListener('click', () => {
            this.showListsView();
        });

        // Lists view controls
        document.getElementById('lists-search').addEventListener('input', (e) => {
            this.searchTerm = e.target.value;
            this.loadListsData();
        });

        document.getElementById('lists-favorites-toggle').addEventListener('click', () => {
            this.showFavoritesOnly = !this.showFavoritesOnly;
            const btn = document.getElementById('lists-favorites-toggle');
            if (this.showFavoritesOnly) {
                btn.classList.add('active');
                btn.textContent = '⭐ Tylko ulubione';
            } else {
                btn.classList.remove('active');
                btn.textContent = '⭐ Ulubione';
            }
            this.loadListsData();
        });

        // Edit properties button
        document.getElementById('edit-properties').addEventListener('click', () => {
            if (this.currentListKey) {
                this.showPropertiesModal(this.currentListKey);
            }
        });

        // Items view controls
        document.getElementById('items-search').addEventListener('input', (e) => {
            if (this.itemsTable) {
                this.itemsTable.setFilter('content', 'like', e.target.value);
            }
        });

        document.getElementById('items-status-filter').addEventListener('change', (e) => {
            if (this.itemsTable) {
                if (e.target.value === '') {
                    this.itemsTable.removeFilter('status');
                } else {
                    this.itemsTable.setFilter('status', '=', e.target.value);
                }
            }
        });

        // Config modal (keep existing functionality)
        const configBtn = document.getElementById('config-btn');
        const configModal = document.getElementById('config-modal');
        const closeBtns = configModal.querySelectorAll('.close-btn');
        
        configBtn.addEventListener('click', () => {
            configModal.style.display = 'block';
        });

        closeBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                configModal.style.display = 'none';
            });
        });

        window.addEventListener('click', (e) => {
            if (e.target === configModal) {
                configModal.style.display = 'none';
            }
        });
    }

    async showListsView() {
        this.currentView = 'lists';
        this.currentListKey = null;
        
        // Update UI
        document.getElementById('lists-view').style.display = 'block';
        document.getElementById('list-details-view').style.display = 'none';
        
        // Update breadcrumb
        const breadcrumb = document.getElementById('breadcrumb');
        breadcrumb.innerHTML = '<span class="breadcrumb-item active">📋 Wszystkie listy</span>';
        
        await this.initListsTable();
        await this.loadListsData();
    }

    async showListDetailsView(listKey) {
        console.log('showListDetailsView called with:', listKey); // Debug log
        this.currentView = 'list-details';
        this.currentListKey = listKey;
        
        // Update UI
        document.getElementById('lists-view').style.display = 'none';
        document.getElementById('list-details-view').style.display = 'block';
        
        try {
            // Load list details
            const response = await fetch(`/api/lists/${listKey}`);
            const result = await response.json();
            
            if (result.success) {
                const list = result.list;
                
                // Update breadcrumb
                const breadcrumb = document.getElementById('breadcrumb');
                breadcrumb.innerHTML = `
                    <span class="breadcrumb-item" id="back-to-lists-breadcrumb">📋 Wszystkie listy</span>
                    <span class="breadcrumb-separator"> → </span>
                    <span class="breadcrumb-item active">📄 ${list.title}</span>
                `;
                
                // Add click handler for breadcrumb
                document.getElementById('back-to-lists-breadcrumb').addEventListener('click', () => {
                    this.showListsView();
                });
                
                // Update list header
                document.getElementById('list-title').textContent = list.title;
                document.getElementById('list-description').textContent = list.description || '';
                
                // Load and display all properties
                try {
                    const propsResponse = await fetch(`/api/lists/${listKey}/properties`);
                    const propsResult = await propsResponse.json();
                    
                    const propertiesEl = document.getElementById('list-properties');
                    propertiesEl.innerHTML = '';
                    
                    if (propsResult.success && propsResult.properties && Object.keys(propsResult.properties).length > 0) {
                        Object.entries(propsResult.properties).forEach(([key, value]) => {
                            const tag = document.createElement('span');
                            tag.className = `property-tag ${key === 'is_favorite' ? 'favorite' : ''}`;
                            tag.textContent = `${key}=${value}`;
                            propertiesEl.appendChild(tag);
                        });
                    } else {
                        propertiesEl.innerHTML = '<span style="color: #999; font-style: italic;">brak properties</span>';
                    }
                } catch (error) {
                    console.warn('Could not load properties for list details:', error);
                    const propertiesEl = document.getElementById('list-properties');
                    propertiesEl.innerHTML = '<span style="color: #999;">błąd ładowania properties</span>';
                }
                
                await this.initItemsTable();
                await this.loadItemsData();
                
            } else {
                this.showToast('Błąd podczas ładowania szczegółów listy', 'error');
                this.showListsView();
            }
        } catch (error) {
            console.error('Error loading list details:', error);
            this.showToast('Błąd połączenia', 'error');
            this.showListsView();
        }
    }

    async initListsTable() {
        console.log('initListsTable called'); // Debug log
        if (this.listsTable) {
            this.listsTable.destroy();
        }

        console.log('Creating new Tabulator...'); // Debug log
        
        // Check if Tabulator is available
        if (typeof Tabulator === 'undefined') {
            console.error('Tabulator is not loaded! Creating fallback table...');
            this.createFallbackTable();
            return;
        }
        
        console.log('Tabulator is available, creating table...');
        this.listsTable = new Tabulator("#lists-table", {
            height: "500px",
            layout: "fitColumns",
            responsiveLayout: "hide",
            placeholder: "Brak list do wyświetlenia",
            selectable: true,
            columns: [
                {
                    title: "⭐",
                    field: "is_favorite",
                    width: 40,
                    hozAlign: "center",
                    responsive: 0,
                    formatter: (cell) => cell.getValue() ? "⭐" : "☆",
                    cellClick: (e, cell) => {
                        this.toggleFavorite(cell.getRow().getData().list_key);
                    }
                },
                {
                    title: "📋 Lista",
                    field: "title",
                    minWidth: 200,
                    responsive: 0,
                    formatter: (cell, formatterParams, onRendered) => {
                        const data = cell.getRow().getData();
                        return `<strong style="cursor: pointer;">${data.title}</strong>` + 
                               (data.description ? `<br><small style="color: #666;">${data.description}</small>` : '');
                    },
                    cellClick: (e, cell) => {
                        const listKey = cell.getRow().getData().list_key;
                        console.log('Title cell clicked:', listKey); // Debug log
                        this.showListDetailsView(listKey);
                    }
                },
                {
                    title: "📊 Postęp",
                    field: "completion_percentage",
                    width: 120,
                    responsive: 2,
                    formatter: (cell) => {
                        const percentage = cell.getValue();
                        return `
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${percentage}%"></div>
                            </div>
                            <small>${percentage}%</small>
                        `;
                    }
                },
                {
                    title: "📈 Statusy",
                    field: "status_counts",
                    width: 150,
                    responsive: 3,
                    formatter: (cell, formatterParams, onRendered) => {
                        const data = cell.getRow().getData();
                        return `
                            <div class="status-counts">
                                ${data.pending_items > 0 ? `<span class="status-count pending"><span class="dot"></span>${data.pending_items}</span>` : ''}
                                ${data.in_progress_items > 0 ? `<span class="status-count in-progress"><span class="dot"></span>${data.in_progress_items}</span>` : ''}
                                ${data.completed_items > 0 ? `<span class="status-count completed"><span class="dot"></span>${data.completed_items}</span>` : ''}
                                ${data.failed_items > 0 ? `<span class="status-count failed"><span class="dot"></span>${data.failed_items}</span>` : ''}
                            </div>
                        `;
                    }
                },
                {
                    title: "🔢 Itemy",
                    field: "total_items",
                    width: 80,
                    responsive: 3,
                    hozAlign: "center"
                },
                {
                    title: "📅 Ostatnia aktywność",
                    field: "updated_at",
                    width: 150,
                    responsive: 4,
                    formatter: (cell) => {
                        return this.formatDate(cell.getValue());
                    }
                }
            ],
            rowClick: (e, row) => {
                e.stopPropagation();
                const listKey = row.getData().list_key;
                console.log('List clicked:', listKey); // Debug log
                this.showListDetailsView(listKey);
            },
            rowSelected: (row) => {
                const listKey = row.getData().list_key;
                console.log('List selected:', listKey); // Debug log
                this.showListDetailsView(listKey);
            },
            rowDblClick: (e, row) => {
                // Double-click to open list properties modal
                const listKey = row.getData().list_key;
                this.showPropertiesModal(listKey);
            },
            locale: "pl"
        });
    }

    async initItemsTable() {
        if (this.itemsTable) {
            this.itemsTable.destroy();
        }

        this.itemsTable = new Tabulator("#items-table", {
            height: "600px",
            layout: "fitColumns",
            responsiveLayout: "hide",
            placeholder: "Brak itemów do wyświetlenia",
            columns: [
                {
                    title: "🔽",
                    field: "expand",
                    width: 40,
                    responsive: 0,
                    formatter: (cell) => {
                        const data = cell.getRow().getData();
                        const hasSubitems = data.subitems_count > 0;
                        if (hasSubitems) {
                            return '<span class="expand-icon">▶️</span>';
                        }
                        return '';
                    },
                    cellClick: (e, cell) => {
                        this.toggleSubitems(cell.getRow());
                    }
                },
                {
                    title: "📝 Klucz",
                    field: "item_key",
                    width: 120,
                    responsive: 1,
                    editor: "input"
                },
                {
                    title: "📄 Treść",
                    field: "content",
                    minWidth: 200,
                    responsive: 0,
                    editor: "textarea"
                },
                {
                    title: "📊 Status",
                    field: "status",
                    width: 120,
                    responsive: 0,
                    editor: "list",
                    editorParams: {
                        values: {
                            "pending": "Oczekujące",
                            "in_progress": "W trakcie",
                            "completed": "Ukończone",
                            "failed": "Nieudane"
                        }
                    },
                    formatter: (cell) => this.formatStatus(cell.getValue())
                },
                {
                    title: "🔸 Sub",
                    field: "subitems_count",
                    width: 60,
                    responsive: 2,
                    hozAlign: "center",
                    formatter: (cell) => {
                        const count = cell.getValue();
                        return count > 0 ? count : '';
                    }
                },
                {
                    title: "#️⃣ Poz",
                    field: "position",
                    width: 60,
                    responsive: 3,
                    hozAlign: "center",
                    editor: "number"
                }
            ],
            cellEdited: (cell) => {
                this.handleItemCellEdit(cell);
            },
            rowDblClick: (e, row) => {
                // Double-click to open properties modal
                const data = row.getData();
                this.showItemPropertiesModal(this.currentListKey, data.item_key);
            },
            locale: "pl"
        });
    }

    toggleSubitems(parentRow) {
        const data = parentRow.getData();
        const rowElement = parentRow.getElement();
        const expandIcon = rowElement.querySelector('.expand-icon');
        const existingNested = rowElement.querySelector('.nested-table');
        
        if (existingNested) {
            // Close subitems
            existingNested.remove();
            expandIcon.textContent = '▶️';
        } else {
            // Open subitems
            expandIcon.textContent = '🔽';
            this.createSubitemTable(parentRow, data.subitems);
        }
    }

    createSubitemTable(parentRow, subitems) {
        const parentData = parentRow.getData();
        
        // Create container for nested table
        const holderEl = document.createElement("div");
        
        // Add parent item properties header
        const parentPropsEl = document.createElement("div");
        parentPropsEl.className = "parent-item-header";
        parentPropsEl.style.padding = "5px 10px";
        parentPropsEl.style.backgroundColor = "#e9ecef";
        parentPropsEl.style.borderBottom = "1px solid #dee2e6";
        parentPropsEl.style.fontSize = "12px";
        parentPropsEl.style.color = "#495057";
        
        const propsCount = parentData.properties_count || 0;
        parentPropsEl.innerHTML = `
            <strong>${parentData.item_key}</strong> - Properties: 
            ${propsCount > 0 ? 
                `<span class="props-link" onclick="app.showItemPropertiesModal('${this.currentListKey}', '${parentData.item_key}')" style="color: #007bff; cursor: pointer; text-decoration: underline;">${propsCount} właściwości</span>` : 
                '<span style="color: #6c757d;">brak properties</span>'
            }
        `;
        
        const tableEl = document.createElement("div");
        
        holderEl.className = "nested-table";
        holderEl.style.padding = "0 20px 10px 50px";
        holderEl.style.backgroundColor = "#f8f9fa";
        holderEl.style.borderLeft = "3px solid #007bff";
        
        holderEl.appendChild(parentPropsEl);
        holderEl.appendChild(tableEl);
        parentRow.getElement().appendChild(holderEl);

        // Create nested Tabulator table
        const subTable = new Tabulator(tableEl, {
            layout: "fitColumns",
            data: subitems,
            height: Math.min(250, subitems.length * 40 + 50),
            columns: [
                {
                    title: "🔸 Klucz",
                    field: "item_key",
                    width: 120,
                    editor: "input"
                },
                {
                    title: "📄 Treść",
                    field: "content",
                    minWidth: 180,
                    editor: "textarea"
                },
                {
                    title: "📊 Status",
                    field: "status",
                    width: 120,
                    editor: "list",
                    editorParams: {
                        values: {
                            "pending": "Oczekujące",
                            "in_progress": "W trakcie",
                            "completed": "Ukończone",
                            "failed": "Nieudane"
                        }
                    },
                    formatter: (cell) => this.formatStatus(cell.getValue())
                },
                {
                    title: "⚙️ Properties",
                    field: "properties",
                    width: 80,
                    formatter: () => '<span class="subitem-props-btn">⚙️</span>',
                    cellClick: (e, cell) => {
                        const subitemData = cell.getRow().getData();
                        const parentData = parentRow.getData();
                        this.showSubitemPropertiesModal(this.currentListKey, parentData.item_key, subitemData.item_key);
                    }
                },
                {
                    title: "#️⃣ Poz",
                    field: "position",
                    width: 60,
                    hozAlign: "center",
                    editor: "number"
                }
            ],
            cellEdited: (cell) => {
                this.handleSubitemEdit(parentRow.getData(), cell);
            }
        });
    }

    createFallbackTable() {
        console.log('Creating fallback HTML table...');
        const container = document.getElementById('lists-table');
        container.innerHTML = `
            <div style="padding: 20px; border: 1px solid #ddd; background: white;">
                <h3>Lista TODO (fallback)</h3>
                <p>Tabulator nie załadował się, ładuję dane bezpośrednio...</p>
                <div id="fallback-lists"></div>
            </div>
        `;
        
        // Load data directly
        this.loadFallbackData();
    }
    
    async loadFallbackData() {
        try {
            const response = await fetch('/api/lists?limit=10');
            const result = await response.json();
            console.log('Fallback data loaded:', result);
            
            if (result.success && result.data) {
                const container = document.getElementById('fallback-lists');
                const html = result.data.map(list => 
                    `<div style="border: 1px solid #ccc; margin: 5px; padding: 10px; cursor: pointer;" 
                          onclick="app.showListDetailsView('${list.list_key}')">
                        <strong>${list.title}</strong> (${list.total_items} items)
                     </div>`
                ).join('');
                container.innerHTML = html;
            }
        } catch (error) {
            console.error('Error loading fallback data:', error);
        }
    }

    async loadListsData() {
        console.log('loadListsData called'); // Debug log
        this.showLoading();
        try {
            const params = new URLSearchParams({
                limit: this.pageSize,
                offset: this.currentPage * this.pageSize,
                search: this.searchTerm,
                favorites_only: this.showFavoritesOnly
            });

            console.log('Fetching lists...'); // Debug log
            const response = await fetch(`/api/lists?${params}`);
            const result = await response.json();
            console.log('Lists loaded:', result.data?.length || 0, 'lists'); // Debug log
            
            if (result.success) {
                this.listsTable.setData(result.data);
                this.updateListsPagination(result.pagination);
            } else {
                this.showToast('Błąd podczas ładowania list', 'error');
            }
        } catch (error) {
            console.error('Error loading lists:', error);
            this.showToast('Błąd połączenia', 'error');
        }
        this.hideLoading();
    }

    async loadItemsData() {
        if (!this.currentListKey) return;
        
        this.showLoading();
        try {
            const response = await fetch(`/api/lists/${this.currentListKey}/items`);
            const result = await response.json();
            
            if (result.success) {
                this.itemsTable.setData(result.data);
                this.updateItemsPagination(result.pagination);
            } else {
                this.showToast('Błąd podczas ładowania itemów', 'error');
            }
        } catch (error) {
            console.error('Error loading items:', error);
            this.showToast('Błąd połączenia', 'error');
        }
        this.hideLoading();
    }

    updateListsPagination(pagination) {
        const container = document.getElementById('lists-pagination');
        if (!pagination) {
            container.style.display = 'none';
            return;
        }
        
        container.style.display = 'flex';
        const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;
        const totalPages = Math.ceil(pagination.total / pagination.limit);
        
        container.innerHTML = `
            <div class="pagination-info">
                Strona ${currentPage} z ${totalPages} (${pagination.total} list)
            </div>
            <div class="pagination-controls">
                <button class="pagination-btn" ${currentPage <= 1 ? 'disabled' : ''} onclick="app.goToListsPage(${currentPage - 2})">‹</button>
                ${this.generatePageButtons(currentPage, totalPages, 'app.goToListsPage')}
                <button class="pagination-btn" ${!pagination.has_more ? 'disabled' : ''} onclick="app.goToListsPage(${currentPage})">›</button>
            </div>
        `;
    }

    updateItemsPagination(pagination) {
        const container = document.getElementById('items-pagination');
        if (!pagination) {
            container.style.display = 'none';
            return;
        }
        
        container.style.display = 'flex';
        const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;
        const totalPages = Math.ceil(pagination.total / pagination.limit);
        
        container.innerHTML = `
            <div class="pagination-info">
                Strona ${currentPage} z ${totalPages} (${pagination.total} itemów)
            </div>
            <div class="pagination-controls">
                <button class="pagination-btn" ${currentPage <= 1 ? 'disabled' : ''} onclick="app.goToItemsPage(${currentPage - 2})">‹</button>
                ${this.generatePageButtons(currentPage, totalPages, 'app.goToItemsPage')}
                <button class="pagination-btn" ${!pagination.has_more ? 'disabled' : ''} onclick="app.goToItemsPage(${currentPage})">›</button>
            </div>
        `;
    }

    generatePageButtons(currentPage, totalPages, clickHandler) {
        let buttons = '';
        const maxButtons = 5;
        let start = Math.max(1, currentPage - Math.floor(maxButtons / 2));
        let end = Math.min(totalPages, start + maxButtons - 1);
        
        if (end - start < maxButtons - 1) {
            start = Math.max(1, end - maxButtons + 1);
        }
        
        for (let i = start; i <= end; i++) {
            buttons += `<button class="pagination-btn ${i === currentPage ? 'active' : ''}" onclick="${clickHandler}(${i - 1})">${i}</button>`;
        }
        
        return buttons;
    }

    goToListsPage(page) {
        this.currentPage = page;
        this.loadListsData();
    }

    goToItemsPage(page) {
        // Items pagination would go here when implemented
        // For now, Tabulator handles it client-side
    }

    async toggleFavorite(listKey) {
        try {
            const response = await fetch(`/api/lists/${listKey}/favorite`, {
                method: 'POST'
            });

            const result = await response.json();
            if (result.success) {
                this.showToast(result.message, 'success');
                await this.loadListsData(); // Refresh data
            } else {
                this.showToast('Błąd podczas zmiany ulubionych', 'error');
            }
        } catch (error) {
            console.error('Failed to toggle favorite:', error);
            this.showToast('Błąd połączenia', 'error');
        }
    }

    async handleItemCellEdit(cell) {
        const data = cell.getRow().getData();
        const field = cell.getField();
        const value = cell.getValue();

        try {
            const updateData = {};
            updateData[field] = value;

            const response = await fetch(`/api/items/${this.currentListKey}/${data.item_key}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updateData)
            });

            const result = await response.json();
            if (result.success) {
                this.showToast('Zaktualizowano pomyślnie', 'success');
            } else {
                this.showToast('Błąd podczas aktualizacji', 'error');
                cell.restoreOldValue();
            }
        } catch (error) {
            console.error('Failed to update item:', error);
            this.showToast('Błąd połączenia', 'error');
            cell.restoreOldValue();
        }
    }

    async handleSubitemEdit(parentData, cell) {
        const subitemData = cell.getRow().getData();
        const field = cell.getField();
        const value = cell.getValue();

        try {
            const updateData = {};
            updateData[field] = value;

            const response = await fetch(`/api/subitems/${this.currentListKey}/${parentData.item_key}/${subitemData.item_key}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updateData)
            });

            const result = await response.json();
            if (result.success) {
                this.showToast('Subitem zaktualizowany', 'success');
            } else {
                this.showToast('Błąd podczas aktualizacji subitemu', 'error');
                cell.restoreOldValue();
            }
        } catch (error) {
            console.error('Failed to update subitem:', error);
            this.showToast('Błąd połączenia', 'error');
            cell.restoreOldValue();
        }
    }

    formatStatus(status) {
        const statusMap = {
            'pending': '<span class="status-badge status-pending">Oczekujące</span>',
            'in_progress': '<span class="status-badge status-in-progress">W trakcie</span>',
            'completed': '<span class="status-badge status-completed">Ukończone</span>',
            'failed': '<span class="status-badge status-failed">Nieudane</span>'
        };
        return statusMap[status] || status;
    }

    formatDate(dateString) {
        if (!dateString) return '';
        try {
            const date = new Date(dateString);
            const now = new Date();
            const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
            
            if (diffDays === 0) return 'dziś';
            if (diffDays === 1) return 'wczoraj';
            if (diffDays < 7) return `${diffDays} dni temu`;
            
            return date.toLocaleDateString('pl-PL', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
        } catch {
            return dateString;
        }
    }

    showLoading() {
        document.getElementById('loading').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }

    async showPropertiesModal(listKey) {
        try {
            // Get current properties
            const response = await fetch(`/api/lists/${listKey}/properties`);
            const result = await response.json();
            
            if (!result.success) {
                this.showToast('Błąd podczas pobierania properties', 'error');
                return;
            }
            
            const properties = result.properties || {};
            
            // Create modal HTML
            const modalHTML = `
                <div id="properties-modal" class="modal" style="display: block;">
                    <div class="modal-content" style="max-width: 500px;">
                        <div class="modal-header">
                            <h2>⚙️ Properties - ${listKey}</h2>
                            <button class="close-btn">✖️</button>
                        </div>
                        <div class="modal-body">
                            <div id="properties-list" class="properties-form">
                                ${Object.entries(properties).map(([key, value]) => `
                                    <div class="property-row">
                                        <input type="text" class="property-key" value="${key}" placeholder="klucz" />
                                        <input type="text" class="property-value" value="${value}" placeholder="wartość" />
                                        <button class="btn btn-danger delete-property" data-key="${key}">🗑️</button>
                                    </div>
                                `).join('')}
                                <div class="property-row new-property">
                                    <input type="text" class="property-key" placeholder="nowy klucz" />
                                    <input type="text" class="property-value" placeholder="wartość" />
                                    <button class="btn btn-primary add-property">➕</button>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button id="save-properties" class="btn btn-primary">✅ Zapisz</button>
                            <button class="close-btn btn btn-secondary">❌ Anuluj</button>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal if any
            const existingModal = document.getElementById('properties-modal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add modal to DOM
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            
            // Setup modal event handlers
            this.setupPropertiesModal(listKey);
            
        } catch (error) {
            console.error('Error showing properties modal:', error);
            this.showToast('Błąd połączenia', 'error');
        }
    }

    setupPropertiesModal(listKey) {
        const modal = document.getElementById('properties-modal');
        
        // Close button handlers
        modal.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                modal.remove();
            });
        });
        
        // Click outside to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        // Add property button
        modal.querySelector('.add-property').addEventListener('click', () => {
            const newRow = modal.querySelector('.new-property');
            const key = newRow.querySelector('.property-key').value.trim();
            const value = newRow.querySelector('.property-value').value.trim();
            
            if (key) {
                const propertiesList = modal.querySelector('#properties-list');
                const propertyRow = document.createElement('div');
                propertyRow.className = 'property-row';
                propertyRow.innerHTML = `
                    <input type="text" class="property-key" value="${key}" placeholder="klucz" />
                    <input type="text" class="property-value" value="${value}" placeholder="wartość" />
                    <button class="btn btn-danger delete-property" data-key="${key}">🗑️</button>
                `;
                propertiesList.insertBefore(propertyRow, newRow);
                
                // Setup delete button
                propertyRow.querySelector('.delete-property').addEventListener('click', () => {
                    propertyRow.remove();
                });
                
                // Clear new property inputs
                newRow.querySelector('.property-key').value = '';
                newRow.querySelector('.property-value').value = '';
            }
        });
        
        // Delete property buttons
        modal.querySelectorAll('.delete-property').forEach(btn => {
            btn.addEventListener('click', () => {
                btn.parentElement.remove();
            });
        });
        
        // Save properties button
        modal.querySelector('#save-properties').addEventListener('click', async () => {
            await this.saveProperties(listKey);
            modal.remove();
        });
    }

    async saveProperties(listKey) {
        const modal = document.getElementById('properties-modal');
        const propertyRows = modal.querySelectorAll('.property-row:not(.new-property)');
        
        try {
            this.showLoading();
            
            // Get all current properties to compare and delete removed ones
            const currentResponse = await fetch(`/api/lists/${listKey}/properties`);
            const currentResult = await currentResponse.json();
            const currentProps = currentResult.success ? currentResult.properties : {};
            
            // Collect new properties from form
            const newProps = {};
            propertyRows.forEach(row => {
                const key = row.querySelector('.property-key').value.trim();
                const value = row.querySelector('.property-value').value.trim();
                if (key) {
                    newProps[key] = value;
                }
            });
            
            // Delete removed properties
            for (const key of Object.keys(currentProps)) {
                if (!(key in newProps)) {
                    await fetch(`/api/lists/${listKey}/properties/${key}`, {
                        method: 'DELETE'
                    });
                }
            }
            
            // Set/update properties
            for (const [key, value] of Object.entries(newProps)) {
                await fetch(`/api/lists/${listKey}/properties`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, value })
                });
            }
            
            this.showToast('Properties zaktualizowane', 'success');
            await this.loadListsData(); // Refresh lists view
            
            // Refresh list details if we're in that view
            if (this.currentView === 'list-details' && this.currentListKey === listKey) {
                await this.showListDetailsView(listKey);
            }
            
        } catch (error) {
            console.error('Error saving properties:', error);
            this.showToast('Błąd podczas zapisywania', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async showItemPropertiesModal(listKey, itemKey) {
        try {
            // Get current properties
            const response = await fetch(`/api/lists/${listKey}/items/${itemKey}/properties`);
            const result = await response.json();
            
            if (!result.success) {
                this.showToast('Błąd podczas pobierania properties itemu', 'error');
                return;
            }
            
            const properties = result.properties || {};
            
            // Create modal HTML
            const modalHTML = `
                <div id="item-properties-modal" class="modal" style="display: block;">
                    <div class="modal-content" style="max-width: 600px;">
                        <div class="modal-header">
                            <h2>⚙️ Properties - ${itemKey}</h2>
                            <button class="close-btn">✖️</button>
                        </div>
                        <div class="modal-body">
                            <div id="item-properties-list" class="properties-form">
                                ${Object.entries(properties).map(([key, value]) => `
                                    <div class="property-row">
                                        <input type="text" class="property-key" value="${key}" placeholder="klucz" />
                                        <input type="text" class="property-value" value="${value}" placeholder="wartość" />
                                        <button class="btn btn-danger delete-property" data-key="${key}">🗑️</button>
                                    </div>
                                `).join('')}
                                <div class="property-row new-property">
                                    <input type="text" class="property-key" placeholder="nowy klucz" />
                                    <input type="text" class="property-value" placeholder="wartość" />
                                    <button class="btn btn-primary add-property">➕</button>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button id="save-item-properties" class="btn btn-primary">✅ Zapisz</button>
                            <button class="close-btn btn btn-secondary">❌ Anuluj</button>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal if any
            const existingModal = document.getElementById('item-properties-modal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add modal to DOM
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            
            // Setup modal event handlers
            this.setupItemPropertiesModal(listKey, itemKey);
            
        } catch (error) {
            console.error('Error showing item properties modal:', error);
            this.showToast('Błąd połączenia', 'error');
        }
    }

    setupItemPropertiesModal(listKey, itemKey) {
        const modal = document.getElementById('item-properties-modal');
        
        // Close button handlers
        modal.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                modal.remove();
            });
        });
        
        // Click outside to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        // Add property button
        modal.querySelector('.add-property').addEventListener('click', () => {
            const newRow = modal.querySelector('.new-property');
            const key = newRow.querySelector('.property-key').value.trim();
            const value = newRow.querySelector('.property-value').value.trim();
            
            if (key) {
                const propertiesList = modal.querySelector('#item-properties-list');
                const propertyRow = document.createElement('div');
                propertyRow.className = 'property-row';
                propertyRow.innerHTML = `
                    <input type="text" class="property-key" value="${key}" placeholder="klucz" />
                    <input type="text" class="property-value" value="${value}" placeholder="wartość" />
                    <button class="btn btn-danger delete-property" data-key="${key}">🗑️</button>
                `;
                propertiesList.insertBefore(propertyRow, newRow);
                
                // Setup delete button
                propertyRow.querySelector('.delete-property').addEventListener('click', () => {
                    propertyRow.remove();
                });
                
                // Clear new property inputs
                newRow.querySelector('.property-key').value = '';
                newRow.querySelector('.property-value').value = '';
            }
        });
        
        // Delete property buttons
        modal.querySelectorAll('.delete-property').forEach(btn => {
            btn.addEventListener('click', () => {
                btn.parentElement.remove();
            });
        });
        
        // Save properties button
        modal.querySelector('#save-item-properties').addEventListener('click', async () => {
            await this.saveItemProperties(listKey, itemKey);
            modal.remove();
        });
    }

    async saveItemProperties(listKey, itemKey) {
        const modal = document.getElementById('item-properties-modal');
        const propertyRows = modal.querySelectorAll('.property-row:not(.new-property)');
        
        try {
            this.showLoading();
            
            // Collect new properties from form
            const newProps = {};
            propertyRows.forEach(row => {
                const key = row.querySelector('.property-key').value.trim();
                const value = row.querySelector('.property-value').value.trim();
                if (key) {
                    newProps[key] = value;
                }
            });
            
            // Set/update properties
            for (const [key, value] of Object.entries(newProps)) {
                await fetch(`/api/lists/${listKey}/items/${itemKey}/properties`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, value })
                });
            }
            
            this.showToast('Properties itemu zaktualizowane', 'success');
            await this.loadItemsData(); // Refresh items view
            
        } catch (error) {
            console.error('Error saving item properties:', error);
            this.showToast('Błąd podczas zapisywania', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async showSubitemPropertiesModal(listKey, itemKey, subitemKey) {
        try {
            // Get current properties
            const response = await fetch(`/api/lists/${listKey}/items/${itemKey}/subitems/${subitemKey}/properties`);
            const result = await response.json();
            
            if (!result.success) {
                this.showToast('Błąd podczas pobierania properties subitemu', 'error');
                return;
            }
            
            const properties = result.properties || {};
            
            // Create modal HTML
            const modalHTML = `
                <div id="subitem-properties-modal" class="modal" style="display: block;">
                    <div class="modal-content" style="max-width: 600px;">
                        <div class="modal-header">
                            <h2>⚙️ Properties - ${subitemKey}</h2>
                            <button class="close-btn">✖️</button>
                        </div>
                        <div class="modal-body">
                            <div id="subitem-properties-list" class="properties-form">
                                ${Object.entries(properties).map(([key, value]) => `
                                    <div class="property-row">
                                        <input type="text" class="property-key" value="${key}" placeholder="klucz" />
                                        <input type="text" class="property-value" value="${value}" placeholder="wartość" />
                                        <button class="btn btn-danger delete-property" data-key="${key}">🗑️</button>
                                    </div>
                                `).join('')}
                                <div class="property-row new-property">
                                    <input type="text" class="property-key" placeholder="nowy klucz" />
                                    <input type="text" class="property-value" placeholder="wartość" />
                                    <button class="btn btn-primary add-property">➕</button>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button id="save-subitem-properties" class="btn btn-primary">✅ Zapisz</button>
                            <button class="close-btn btn btn-secondary">❌ Anuluj</button>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal if any
            const existingModal = document.getElementById('subitem-properties-modal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add modal to DOM
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            
            // Setup modal event handlers
            this.setupSubitemPropertiesModal(listKey, itemKey, subitemKey);
            
        } catch (error) {
            console.error('Error showing subitem properties modal:', error);
            this.showToast('Błąd połączenia', 'error');
        }
    }

    setupSubitemPropertiesModal(listKey, itemKey, subitemKey) {
        const modal = document.getElementById('subitem-properties-modal');
        
        // Close button handlers
        modal.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                modal.remove();
            });
        });
        
        // Click outside to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        // Add property button
        modal.querySelector('.add-property').addEventListener('click', () => {
            const newRow = modal.querySelector('.new-property');
            const key = newRow.querySelector('.property-key').value.trim();
            const value = newRow.querySelector('.property-value').value.trim();
            
            if (key) {
                const propertiesList = modal.querySelector('#subitem-properties-list');
                const propertyRow = document.createElement('div');
                propertyRow.className = 'property-row';
                propertyRow.innerHTML = `
                    <input type="text" class="property-key" value="${key}" placeholder="klucz" />
                    <input type="text" class="property-value" value="${value}" placeholder="wartość" />
                    <button class="btn btn-danger delete-property" data-key="${key}">🗑️</button>
                `;
                propertiesList.insertBefore(propertyRow, newRow);
                
                // Setup delete button
                propertyRow.querySelector('.delete-property').addEventListener('click', () => {
                    propertyRow.remove();
                });
                
                // Clear new property inputs
                newRow.querySelector('.property-key').value = '';
                newRow.querySelector('.property-value').value = '';
            }
        });
        
        // Delete property buttons
        modal.querySelectorAll('.delete-property').forEach(btn => {
            btn.addEventListener('click', () => {
                btn.parentElement.remove();
            });
        });
        
        // Save properties button
        modal.querySelector('#save-subitem-properties').addEventListener('click', async () => {
            await this.saveSubitemProperties(listKey, itemKey, subitemKey);
            modal.remove();
        });
    }

    async saveSubitemProperties(listKey, itemKey, subitemKey) {
        const modal = document.getElementById('subitem-properties-modal');
        const propertyRows = modal.querySelectorAll('.property-row:not(.new-property)');
        
        try {
            this.showLoading();
            
            // Collect new properties from form
            const newProps = {};
            propertyRows.forEach(row => {
                const key = row.querySelector('.property-key').value.trim();
                const value = row.querySelector('.property-value').value.trim();
                if (key) {
                    newProps[key] = value;
                }
            });
            
            // Set/update properties
            for (const [key, value] of Object.entries(newProps)) {
                await fetch(`/api/lists/${listKey}/items/${itemKey}/subitems/${subitemKey}/properties`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, value })
                });
            }
            
            this.showToast('Properties subitemu zaktualizowane', 'success');
            await this.loadItemsData(); // Refresh items view
            
        } catch (error) {
            console.error('Error saving subitem properties:', error);
            this.showToast('Błąd podczas zapisywania', 'error');
        } finally {
            this.hideLoading();
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 10);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    container.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, creating app...'); // Debug log
    try {
        window.app = new TodoAppNew();
        console.log('App created successfully:', window.app); // Debug log
    } catch (error) {
        console.error('Error creating app:', error); // Debug log
    }
});