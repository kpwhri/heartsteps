
export class Notification {

    public id: string;
    public title: string;
    public body: string;

    constructor(
        id: string,
        title: string,
        body: string
    ) {
        this.id = id;
        this.title = title;
        this.body = body;
    }
}