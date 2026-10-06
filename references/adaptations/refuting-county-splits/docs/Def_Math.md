* Dividir un estado en distritros
  * Un estado de 15 condados en 3 distritos

  $$
   G = (V,E)
  $$

  $V:$ son los nodos como los condados
  $E:$ son las aristas como las fronteras fisicas que se comparten



Condiciones:

1. Población lo mas similar posible (igual o +/- 1)
2. Formar agrupaciones compactas (conectadas)
3. Formas conectadas
4. No partir los condados por la mitad (No partir una entidad politica a la mitad)


---


**Propuesta preliminar:**
> Un numero $K$ de distritos requiere almenos $k-1$ diviciones de condados

- Contra ejemplo grafico:

Se quieren armar dos distritos de 100 personas exactas

![alt text](image.png)

Se requieren 2 cortes para lograr el objetivo de 2 distritos de 100 personas

Si $k=2$ entonces $2 > k-1$

**Propuesta del articulo:**
> Se pueden hacer redistritaciones con 0 diviciones de condados, muchos estados los permiten


---
Variables a tomar en cuenta:

| Parám | Definición |
| --- | --- |
| $G$ | Grafo base |
| $p_i$ | Población de cada condado o unidad individual |
| $k$ | Número de distritos a crear |
| $L, U$ | Límites superior e inferior de las pobraciones que queremos |


---
Variables de desición:

**$x_{ij}:$** Asignación, es una variable binaria que indica si una unidad entera va hacia un distrito  (Discreta)

**$z_{ij}:$** Variable continua para definir cantidades exactas de pobración

**$S_i:$** Cantidad de diviciones, para penalizar los cortes

---
Hay que minimizar la suma total de las divisiones, para manatener los condados unidos y maximizar las aristas preservadas del grafo para que los distritos resultantes queden bien agrupados y super compactos

> ¿Como se prueba esto ultimo?


---


### Algortimo de recorte progresivo

Descomposición progresiva, ir extrallendo bloques perfectos partiendo de un nodo raiz, bajo la condición de que el grafo conectado se mantiene conectado y correcto para realizar el sigueinte recorte

Los recordes son selectivos a las disponibilidad del grafo complementarios


### Continuidad bajo flujo (Para mantener los distritos conectados)


Si la diferencia del flujo que entra y el flujo que sale de un nodo es 1, entonces el flujo viajo correctamente

Y el flujo solo puede viajar por unidades que realmente pertenescan al distritro

### Desigualdades separadoreas para mantener la integridad del grafo complemenatario
