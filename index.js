let loader_flag = 0;

window.addEventListener('load', () => {
    console.log("Document loaded");
    let mainField = document.querySelector("#detect_field");
    
    mainField.addEventListener("keydown", (e) => {
        
        if (e.code === "Enter") {
            e.preventDefault();
            document.querySelector("#trans_btn").click();
        }
    });
})

const toggleLoader = (loading) => {
    let loader = document.querySelector("#loader");
    loader_flag++;

    if(loading){
        loader.style.display = "inline-block";
    }else if(!loading && loader_flag == 4) {
        loader.style.display = "none";
        loader_flag = 0;
    }
}


const translateHandler = async (q, tl) => {

    let textField = document.querySelector(`#trans_${tl}`);
    
    let trans_response = await fetch(`https://apiml.joeper.myds.me/translate?q=${q}&tl=${tl}`);
    if (trans_response.ok) { // if HTTP-status is 200-299
        let trans_json = await trans_response.json();
        // console.log(trans_json)

        textField.innerText = trans_json.result;
    } else {
        console.error(trans_response);  
    }


    let dict_response = await fetch(`https://apiml.joeper.myds.me/dictionary?q=${q}&tl=${tl}`);
    if (dict_response.ok) { // if HTTP-status is 200-299
        let dict_json = await dict_response.json();
        // console.log(dict_json)

        let similar = document.querySelector(`#similar_list_${tl}`);
        similar.innerHTML = ``;

        dict_json.result.forEach(element => {
            similar.innerHTML += `${element}; `;
        });

        document.querySelector(`#similar_${tl}`).style.display = "block";

    } else {
        let dict_json = await dict_response.json();
        console.log(dict_json);  
        document.querySelector(`#similar_${tl}`).style.display = "none";
    }
    
    toggleLoader(false);
}


const clearText = async () => {
    document.querySelector("#detect_field").value = "";
}


const runTranslation = async () => {
    let mainField = document.querySelector("#detect_field").value;
    
    toggleLoader(true);

    translateHandler(mainField, "eng");
    translateHandler(mainField, "spa");
    translateHandler(mainField, "fre");
    translateHandler(mainField, "deu");

}

