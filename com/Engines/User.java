package com.Engines;
public class User {
    String name;
    int weight;
    int imc;

    public User(String name, int weight, int imc) {
        this.name = name;
        this.weight = weight;
        this.imc = imc;
    }
    
    public void setName(String name) {
        this.name = name;
    }

    public void setWeight(int weight) {
        this.weight = weight;
    }

    public void setImc(int imc) {
        this.imc = imc;
    }    
    
    public String getName() {
        return name;
    }

    public int getWeight() {
        return weight;
    }

    public int getImc(int imc){
        return imc;
    }
}
