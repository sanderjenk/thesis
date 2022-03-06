import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Issue } from './issue';
import { BehaviorSubject } from 'rxjs/internal/BehaviorSubject';
import { map } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class IssuesService {

  public issueHistorySubject = new BehaviorSubject<Issue[]>([]);

  constructor(private http: HttpClient) { }

  getIssues() {
    // return this.http.get<Issue[]>("../../assets/issues.json");
    return this.http.get<string[]>("/api/issues").pipe(
      map(x => x.map(y => 
        {    
          console.log(y)
          var issue = JSON.parse(y)
          issue.priority = issue["priority.name"]
          return issue;
        })));
  }

  generateReccommendations(issues: Issue[]) {
    return this.http.post<string[]>("/api/generate", issues.map(x => x.key)).pipe(
      map(x => x.map(y => 
        {    
          console.log(y)
          var issue = JSON.parse(y)
          issue.priority = issue["priority.name"]
          return issue;
        })));
  }

  addIssueToHistory(issue: Issue) {
    let history = this.issueHistorySubject.getValue();

    if (history.find(x => x.key == issue.key)) return;

    history.push(issue);

    this.issueHistorySubject.next(history);
  }

  remove(key: string) {
    let history = this.issueHistorySubject.getValue();

    let issue = history.find(x => x.key == key);

    if (!issue) return;

    let index = history.indexOf(issue);

    history.splice(index, 1);

    this.issueHistorySubject.next(history);
  }
}
