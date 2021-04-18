console.log("starting main.js");

const { Datastore } = require("@google-cloud/datastore");
// import Datastore from "google-cloud/datastore";

function test() {
  const datastore = new Datastore();
  const getVisits = () => {
    const query = datastore.createQuery("course");

    return datastore.runQuery(query);
  };
  console.log("get visits is:", getVisits);
}

module.exports = { test };

// $(function () {

//     const datastore = new Datastore();
//    const getVisits = () => {
//      const query = datastore
//        .createQuery('course');

//      return datastore.runQuery(query);
//    };
//    console.log("get visits is:", getVisits);
//     var items = {{ course_list| tojson }};

//     function split(val) {
//         return val.split(/,\s*/);
//     }
//     function extractLast(term) {
//         return split(term).pop();
//     }

//     $("#autocomplete")
//         .autocomplete({
//             minLength: 0,
//             source: function (request, response) {
//                 var results = $.ui.autocomplete.filter(
//                     items, extractLast(request.term))
//                 console.log(typeof results)
//                 response(results.slice(0,10));
//             },
//             focus: function () {
//                 return false;
//             },
//             select: function (event, ui) {
//                 var terms = split(this.value);
//                 // remove the current input
//                 terms.pop();
//                 // add the selected item
//                 terms.push(ui.item.value.replace(/,/g, " "));
//                 // add placeholder to get the comma-and-space at the end
//                 terms.push("");
//                 this.value = terms.join(", ");

//                 return false;
//             }
//         });
// });
