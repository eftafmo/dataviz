import NUTS from 'js/constants/nuts.json';


export function get_nuts_label(code) {
  return NUTS[code];
}

export default {
  methods: {
    get_nuts_label,
  }
}
