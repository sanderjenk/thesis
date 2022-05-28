import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject } from 'rxjs/internal/BehaviorSubject';
import { map } from 'rxjs';
import { Issue } from './issue';

@Injectable({
  providedIn: 'root',
})
export class IssuesService {

  public selectedProjectSubject = new BehaviorSubject<string>("");

  public generatedIssuesSubject = new BehaviorSubject<Issue[]>([]);

  constructor(private http: HttpClient) { }

  public baseUrl = "http://localhost/api/";

  getProjects() {
    return this.http.get<string[]>(this.baseUrl + "projects").pipe(
      map(x => x.map(y => JSON.parse(y))));
  }

  getDevelopers() {
    let project = this.selectedProjectSubject.value;
    return this.http.get<string[]>(this.baseUrl + "developers" , {params: {project}});
    }

  generateReccommendations(storypoints: number, developer: string) {
    let project = this.selectedProjectSubject.value;
    return this.http.post<string[]>(this.baseUrl + "generate", {}, {params: {project, storypoints, username: developer}});
  }

  getVelocity(developer: string) {
    let project = this.selectedProjectSubject.value;
    return this.http.get<number>(this.baseUrl + "velocity", {params: {username: developer, project}})
  } 

  selectProject(key: string) {
    this.selectedProjectSubject.next(key);
    this.generatedIssuesSubject.next([])
  }

  submitFeedbackForm(data: any) {
    return this.http.post(this.baseUrl + "feedback", data)
  }
}
