# Einführung
Die beiden Anwendungen sind im Rahmen einer Bachelorarbeit in Informatik an der Universität Heidelberg entstanden. 

Beide Anwendungen sollen dabei helfen LaTeX Dokumente zu parsen und zu visualisieren. 

## Paketabhängigkeiten

Die erste Anwendung (PfP) hilft dabei Paketabhängigkeiten nachzuvollziehen. Dabei kann direkt eine .tex Datei übergeben werden. Hierbei sind keine weitern Hilfsdateien notwendig.

```console
  python3 PfP.py -s <file.tex> 
```

<details>

  <summary> Flags </summary>
  
  **Sourcefile**
  ```console
      python3 PfP.py -s <file.tex> 
  ```
  Diese Flag muss gesetzt sein. Hierbei wird die zu analysierenden Datei angegeben. 
  
  **Input**

  ```console
      python3 PfP.py -s <file.tex>  -i 
  ```
  Dateien welche über Inputs geladen werden, werden nicht im Graphen angezeigt und auch nicht beim Parsen berücksichtigt. (Default=False)


  **Outfile**
  ```console
      python3 PfP.py -s <file.tex>  -outfile <outfilename>
  ```
  Der Name des Graphen kann angepasst werden

  **Browser**
  ```console
      python3 PfP.py -s <file.tex>  -b
  ```
  Das automatische Öffnen des Graphen im Browser kann dadurch gesteuert werden (Default=True)

  **Pipeline**
  ```console
      python3 PfP.py -s <file.tex>  -pipe 
  ```
  Der resultierende Graph wird zusätzlich in eine .dot-Datei umgewandelt. Diese kann dann, zum Beispiel mittels dot2tikz, anderweitig genutzt werden. (Default=False)

  **Testfunktion**
  ```console
      python3 PfP.py -test
  ```
  Diese Falg wird ohne Sourcefile genutzt. Dabei werde alle Pakete, welche von LaTeX installiert wurden getestet. Dies kann eine Weile dauern. (Default=False)
  
</details>

## Skripte

Die zweite Anwendung (PfS) dient dazu Skripte, welche mit LaTeX erstellt werden zu analysieren. Dafür werden Umgebungen und Label genutzt. Die Umgebungen werden dabei von drei Listen gesteuert. 

upper_envs = Diese Umgebungen benötigen eine Umgebungen aus der Liste lower_envs um abgeschlossen zu werden. Andernfalls werden diese Umgebungen durch neue Kapitel geschlossen. Typische Umgebungen sind dabei z.b. Theorem, Definition usw. 

lower_envs = Diese Umgebungen schließen ein Umgebung ab. Hierbei wird in der hinterlegten Baumstruktur auf das Kaptiel zurückgesetzt Typische Umgebungen sind dabei z.b. Proof

banned_envs = Diese Umgebungen werden nicht berücksichtigt.

Alle weitern Umgebungen werden berücksichtigt und auch im Graphen dargestellt.

 ```console
      python3 PfS.py -i <file.tex>
 ```

<details>

<summary> Flags </summary>

  **Sourcefile**
   ```console
      python3 PfS.py -i <file.tex>  
  ```
  Diese Flag muss gesetzt sein. Hierbei wird die zu analysierenden Datei angegeben. 

  **Labels**
   ```console
      python3 PfS.py -i <file.tex> -l 
  ```
  Eine Liste von Labels wird ausgegeben. Dabei wird auch analysiert, welche Labels nicht genutzt werden (Default=False)

  **Baum**
   ```console
      python3 PfS.py -i <file.tex> -t
  ```
  Die erstellte Baumstruktur, wird in der Konsole ausgegeben. (Default=False)

  **Menü**
 ```console
      python3 PfS.py -i <file.tex> -e 
  ```
  Ermöglichte es eigene Umgebungen in die Listen einzufügen. (Default=False)
  
  **Outfile**
  ```console
      python3 PfS.py -i <file.tex>  -g <outfilename>
  ```
  Der Name des Graphen kann angepasst werden

  **Browser**
  ```console
      python3 PfS.py -i <file.tex>  -b
  ```
  Das automatische Öffnen des Graphen im Browser kann dadurch gesteuert werden (Default=True)

  **Pipeline**
  ```console
      python3 PfS.py -i <file.tex>  -pipe 
  ```
  Der resultierende Graph wird zusätzlich in eine .dot-Datei umgewandelt. Diese kann dann, zum Beispiel mittels dot2tikz, anderweitig genutzt werden. (Default=False)

</details>
