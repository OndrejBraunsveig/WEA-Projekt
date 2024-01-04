var json_data;
var todo = ["Vynést koš", "Opravit auto", "Prohrát Lolko"];
var done = ["Odmaturovat", "Koupit byt", "Koupit auto"];

document.addEventListener("DOMContentLoaded", () => {
});

function handleSelector(){
    const selectorButtons = document.querySelectorAll('.selector-btn');

    selectorButtons.forEach(button => {
        button.addEventListener('click', handleButtonClick);
    });

    const doneDiv = document.getElementById('done');
    const todoDiv = document.getElementById('todo');

    const todoBtn = document.getElementById('todoBtn');
    todoBtn.addEventListener('click', () => {
        doneDiv.classList.remove('d-block');
        doneDiv.classList.add('d-none');
        todoDiv.classList.remove('d-none');
        todoDiv.classList.add('d-block');
    });
    const doneBtn = document.getElementById('doneBtn');
    doneBtn.addEventListener('click', () => {
        todoDiv.classList.remove('d-block');
        todoDiv.classList.add('d-none');
        doneDiv.classList.remove('d-none');
        doneDiv.classList.add('d-block');
    });
}

function handleButtonClick(event) {
    const btns = document.querySelectorAll('.selector-btn');
    btns.forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

function generateRows(category, data) {
    const dataDiv = document.getElementById(category);

    // Iterate through the todo list
    data.forEach(item => {
        const rowDiv = document.createElement('div');
        rowDiv.classList.add('d-flex', 'justify-content-between', 'align-items-center', 'px-2','border-bottom', 'border-secondary','rowDiv')
    
        const checkboxDiv = document.createElement('div');
        checkboxDiv.classList.add('form-check');

        const checkboxInput = document.createElement('input');
        checkboxInput.classList.add('form-check-input');
        checkboxInput.setAttribute('type', 'checkbox');
        checkboxInput.setAttribute('value', item);
        checkboxInput.setAttribute('id', item);

        const checkboxText = document.createElement('div');
        checkboxText.classList.add('itemText')
        checkboxText.innerHTML = item;
        checkboxText.contentEditable = 'true';

        // vyresit aby se pri bluru updatoval i list
        checkboxDiv.appendChild(checkboxInput);
        checkboxDiv.appendChild(checkboxText);

        const btnDiv = document.createElement('div');
        btnDiv.classList.add('btn-group', 'hidden', 'btnDiv');
        btnDiv.role = 'group';

        // Convert button
        const convertBtn = document.createElement('button');
        convertBtn.type = 'button';
        convertBtn.classList.add('btn', 'btn-secondary', 'convertBtn');
        convertBtn.innerHTML = 'Convert';
        btnDiv.appendChild(convertBtn);

        // Edit button
        const editBtn = document.createElement('button');
        editBtn.type = 'button';
        editBtn.classList.add('btn', 'btn-secondary', 'editBtn');
        editBtn.innerHTML = 'Edit';
        btnDiv.appendChild(editBtn);

        // Delete button
        const delBtn = document.createElement('button');
        delBtn.type = 'button';
        delBtn.classList.add('btn', 'btn-secondary', 'delBtn');
        delBtn.innerHTML = 'Del';
        btnDiv.appendChild(delBtn);

        rowDiv.appendChild(checkboxDiv);
        rowDiv.appendChild(btnDiv);
        dataDiv.appendChild(rowDiv);

        addDelete(dataDiv, data, item);
        addEdit(dataDiv, data, item);
        addConvert();
        // pridat done/undone tlacitko poslednimu prvku
        // pridat edit poslednimu prvku
        // pridat delete poslednimu prvku
    });
}

function addDelete(parent, data, item){
    const row = parent.lastChild;
    const btn = row.querySelector('.delBtn');
    btn.addEventListener('click', () => {
        const index = data.indexOf(item);
        data.splice(index, 1);
        parent.removeChild(row);
        // tady se bude posilat na backend
    });
}

function addEdit(parent, data, item){
    const row = parent.lastChild;
    const btn = row.querySelector('.editBtn');
    const text = row.querySelector('.itemText');
    btn.addEventListener('click', () => {
        text.contentEditable = 'true';
        text.focus()
    });
    text.addEventListener('keydown', function(event){
        if (event.key == 'Enter') {
            event.preventDefault();
            this.blur();
        }
    });
    text.addEventListener('blur', () => {
        const index = data.indexOf(item);
        data[index] = text.textContent;
        text.contentEditable = 'false';
        // tady se bude posilat na backend
    });
}

function addConvert(parent, data){

}

function handleAddition() {
    const addMenu = document.querySelector('.addMenu');
    addMenu.addEventListener('submit', (e) => {
        e.preventDefault();

        const text = document.getElementById('todoText');
        if (text.value != '') {
            todo.push(text.value);
            generateRows('todo', [text.value]);
            text.value = '';
        }
    });
}
