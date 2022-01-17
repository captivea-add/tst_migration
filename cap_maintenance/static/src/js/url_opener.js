class UrlOpener {

    constructor() {}

    /**
    *   Open all given URLs
    **/
    execute(urls_to_open) {
        var self = this;
        for(var i = 0; i < urls_to_open.length; i++){
            var url = urls_to_open[i];
            window.open(url, '_blank');
        }
        window.close();
    }
}

const url_opener = new UrlOpener();