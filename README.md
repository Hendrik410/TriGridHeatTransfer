# Unstructured Grid Simulations

## Einleitung
Dieses Projekt enth�lt diverse Varianten von Simulationen von W�rmeleitung und Druckver�nderungen in unstrukturierten Dreiecksgittern, sowohl in 2 als auch in 3 Dimensionen.

Die Dateien "visualization.py" und "materials.py" enthalten Methoden und Infoamtionen, die von allen Skripts genutzt werden.
"tri\_grid\_explicit.py" ist der Versuch einer eigenen Implementierung von W�rmeleitung nach der Finiten Volumen Methode.

Alle Dateien die mit dem Prefix "fipy_" beginnen sind Implementierungen auf Basis der FiPy Libraries, einer Bibliothek zum L�sen und Visualisieren von PDEs und ODEs.

## Gitter
In allen Sktipten (bis auf "tri\_grid\_explicit.py") werden die Gitter mit einem Tool namens Gmsh erstellt (Verwendet wurde Version 3.0.4). Gmsh erstellt 2- und 3-Dimensionale Gitter aufgrund von Textbefehlen, die einzelne Geometrien definieren und verkn�pfen.
Zun�chst werden die einzelnen Punkte der Geometrie definiert, dann werden diese Punkte mit Lineien verbunden und diese Linien werden dann zu einer Fl�che verkn�pft.
In den dreidimensionalen F�llen wird diese Fl�che dann noch durch eine Rotation um pi/2 extrudiert, um einen Volumenk�rper zu erhalten.

Um die Randbedingungen sp�ter im Programm festelegen zu k�nnen werden in Gmsh physikalische Kanten (oder Fl�chen) definiert und mit den Namen "inner" und "outer" identifiziert. Im code kann dann mit `mesh.physicalFaces["inner"]` oder `mesh.pyhsicalFaces["outer"]` auf die entsprechenden Fl�chen zugegriffen werden.

Die Gr��e der Zellen wird an den Punkten festgelegt und im Code durch die Variable `cellSize` festgelegt. Diese gibt die Zellgr��e in Metern an und gilt f�r das gesamte Gitter.
Die Koordinaten der Punkte werden dynamisch aufgrund der Angaben �ber die Geometrie (L�ngen und Winkel) bestimmt und das Gitter dementsprechend generiert.

Die Beudeutung der L�ngen `l1`, `l2` und `l3` und der Winkel `alpha` und `beta` ist folgender Sizze zu entnehmen:
![alt text](images/dimensions.png "Dimensionen")


### Achtung
Sind in Gmsh physikalische Kanten (oder Fl�chen) definiert, muss auch die Fl�che (oder das Volumen) als physikalisch markiert werden, da sonst keine Zellen erstellt.


## Randbedingungen

Allen Fl�chen mit der Bezeichnung "inner" wird der Druck `Pres` oder die Temperatur `Ti` zugewiesen, w�hrend alle Fl�chen mit der Bezeichnung "outer" eine Randbedingung mit dem Druck `Pamb` oder der Temperatur `Te` zugewiesen werden. Alle �brigen Zellen werden mit dem Druck `P0`oder der Temperatur `T0` initialisiert.