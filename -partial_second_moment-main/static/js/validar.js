function register(){
    let fullname = document.getElementById("fullname").value;
    let email = document.getElementById("email").value;
    let username = document.getElementById("username").value;
    let country = document.getElementById("country").value;
    let city = document.getElementById("city").value;
    let password = document.getElementById("password").value;
    let typeUsers = document.getElementById("typeUsers").selectedIndex;
    const pattern = new RegExp('^[A-Z]+$', 'i');
    const vemail = new RegExp(/^[a-zA-Z0-9.!#$%&'+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)$/);
    const vpassword = new RegExp(/^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,14}$/);

    if(fullname.length == 0  || fullname== "") {
        alert('Digite el campo Nombre');
        return false;
    }
    if (!pattern.test(fullname)){
        alert('El campo Nombre debe contener solo texto'); 
        return false;
        }
    if (!vemail.test(email)){
        alert('Verifique que el campo email sea correcto'); 
        return false;
        }
    if (username.length == 0  || username== "") {
        alert('Digite el campo Usuario');
        return false;
        }
    // value country
    if (!pattern.test(country)){
        alert('Verifique el campo Pais'); 
        return false;
        }
    // value city
    if (!pattern.test(city)){
        alert('Verifique el campo Ciudad'); 
        return false; 
        }
    //Value password
    if (!vpassword.test(password)){
        alert('El campo password no tiene los caracteres requeridos'); 
        return false;
        }
    if (typeUsers == null || typeUsers == 0 ){
        alert('Por favor selecciona tu tipo de usuario'); 
        return false;
    }
    
}     