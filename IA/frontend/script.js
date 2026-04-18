document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide icons
    lucide.createIcons();

    const itemsList = document.getElementById('items-list');
    const addItemBtn = document.getElementById('add-item-btn');
    const submitBtn = document.getElementById('submit-analysis');
    const resultContainer = document.getElementById('result-container');
    const analysisForm = document.querySelector('.glass-container');
    const resetBtn = document.getElementById('reset-btn');

    // State for items
    let items = [
        { id: Date.now(), name: '', price: '', store: '' }
    ];

    function renderItems() {
        itemsList.innerHTML = '';
        items.forEach((item, index) => {
            const row = document.createElement('div');
            row.className = 'item-row fade-in';
            row.innerHTML = `
                <div class="input-group">
                    <label>Nome do Produto</label>
                    <input type="text" value="${item.name}" placeholder="Ex: Monitor 4K" data-id="${item.id}" data-field="name" class="item-input">
                </div>
                <div class="input-group">
                    <label>Preço</label>
                    <input type="number" value="${item.price}" placeholder="0.00" data-id="${item.id}" data-field="price" class="item-input">
                </div>
                <div class="input-group">
                    <label>Loja</label>
                    <input type="text" value="${item.store}" placeholder="Amazon" data-id="${item.id}" data-field="store" class="item-input">
                </div>
                ${index > 0 ? `<button class="remove-item" data-id="${item.id}"><i data-lucide="trash-2"></i></button>` : '<div></div>'}
            `;
            itemsList.appendChild(row);
        });
        lucide.createIcons();
        attachInputListeners();
    }

    function attachInputListeners() {
        document.querySelectorAll('.item-input').forEach(input => {
            input.addEventListener('input', (e) => {
                const id = parseInt(e.target.dataset.id);
                const field = e.target.dataset.field;
                const item = items.find(i => i.id === id);
                if (item) {
                    item[field] = e.target.value;
                }
            });
        });

        document.querySelectorAll('.remove-item').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = parseInt(e.currentTarget.dataset.id);
                if (items.length > 1) {
                    items = items.filter(i => i.id !== id);
                    renderItems();
                }
            });
        });
    }

    addItemBtn.addEventListener('click', () => {
        items.push({ id: Date.now(), name: '', price: '', store: '' });
        renderItems();
    });

    submitBtn.addEventListener('click', async () => {
        const query = document.getElementById('query').value;
        if (!query) {
            alert('Por favor, informe o que você está procurando.');
            return;
        }

        const validItems = items.filter(i => i.name && i.price).map(i => ({
            name: i.name,
            price: parseFloat(i.price),
            store: i.store || 'Não informada',
            currency: 'BRL'
        }));

        if (validItems.length < 1) {
            alert('Adicione pelo menos um item com nome e preço.');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i data-lucide="loader-2" class="spin"></i> Analisando...';
        lucide.createIcons();

        try {
            const response = await fetch('/api/v1/analysis/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, items: validItems })
            });

            if (!response.ok) throw new Error('Erro na análise');

            const result = await response.json();
            showResult(result);
        } catch (error) {
            alert('Falha ao conectar com o servidor. Verifique se o backend está rodando.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i data-lucide="brain-circuit"></i> Analisar com IA';
            lucide.createIcons();
        }
    });

    function showResult(data) {
        document.getElementById('res-summary').textContent = data.summary;
        document.getElementById('res-best-item').textContent = data.best_value_item || 'N/A';
        document.getElementById('res-savings').textContent = data.savings_potential || 'N/A';
        document.getElementById('res-recommendation').textContent = data.recommendation;
        document.getElementById('confidence-badge').textContent = `${Math.round(data.confidence_score * 100)}% Confiança`;

        analysisForm.classList.add('hidden');
        resultContainer.classList.remove('hidden');
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }

    resetBtn.addEventListener('click', () => {
        resultContainer.classList.add('hidden');
        analysisForm.classList.remove('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Initial render
    renderItems();
});
