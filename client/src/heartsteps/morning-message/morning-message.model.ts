export class MorningMessage {
    id: string;
    date: Date;
    notification: string;
    text: string;
    anchor: string;
    survey: any;
    response: any;

    public isComplete(): boolean {
        console.log("MORNING MSG: from isComplete()");
        if (this.survey) {
            console.log(
                "MORNING MSG: this.survey.completed: ",
                this.survey.completed
            );
        }
        if (this.survey && this.survey.completed) {
            return true;
        } else {
            return false;
        }
    }
}
