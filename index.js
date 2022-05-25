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
    }else if(!loading) {
        loader.style.display = "none";
        loader_flag = 0;
    }
}


const translateHandler = async (q, tl) => {

    tlArray = tl.split(",");
    textFieldArray = [];
    tlArray.forEach(e => {
        textFieldArray.push({"target": e, "element": document.querySelector(`#trans_${e}`)});
    });
    
    // let trans_response = await fetch(`https://apiml.joeper.myds.me/translate?q=${q}&tl=${tl}`);
    let trans_response = await fetch(`http://localhost:8662/translate?q=${q}&tl=${tl}`);
    if (trans_response.ok) { // if HTTP-status is 200-299
        let trans_json = await trans_response.json();
        // console.log(trans_json)

        trans_json.translations.forEach(e => {
            textFieldArray.forEach(textFieldArrayElement => {
                if(e.target == textFieldArrayElement.target){
                    textFieldArrayElement.element.innerHTML = e.result;
                }
            });
        });
        
    } else {
        console.error(trans_response);  
    }


    similarArray = [];
    tlArray.forEach(e => {
        similarArray.push({"target": e, "element": document.querySelector(`#similar_list_${e}`)});
        document.querySelector(`#similar_list_${e}`).innerHTML = "";
        document.querySelector(`#similar_${e}`).style.display = "none";
    });
    
    // let trans_response = await fetch(`https://apiml.joeper.myds.me/translate?q=${q}&tl=${tl}`);
    let dict_response = await fetch(`http://localhost:8662/dictionary?q=${q}&tl=${tl}`);
    if (dict_response.ok) { // if HTTP-status is 200-299
        let dict_json = await dict_response.json();
        // console.log(trans_json)



        dict_json.definitions.forEach(e => {
            similarArray.forEach(similarArrayElement => {
                // console.log(e.target, similarArrayElement.target, similarArrayElement.element.innerHTML);

                if(e.target == similarArrayElement.target){
                    e.result.forEach(def => {
                        // console.log(def)
                        similarArrayElement.element.innerHTML += `${def}; `;
                    });
                    document.querySelector(`#similar_${e.target}`).style.display = "block";
                }
            });
        });
        
    } else {
        let dict_json = await dict_response.json();
        console.log(dict_json);  
    }
    
}


const clearText = async () => {
    document.querySelector("#detect_field").value = "";
}


const runTranslation = async () => {
    let mainField = document.querySelector("#detect_field").value;
    
    toggleLoader(true);

    await translateHandler(mainField, "eng,spa,fre,deu");

    toggleLoader(false);
}

