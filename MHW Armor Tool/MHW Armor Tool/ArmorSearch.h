#pragma once
#include "json.h"
#include <vector>
#include <regex>
#include <ctype.h>

#include <iostream>

using string = std::string;

class ArmorSearch {
public:
	ArmorSearch(Json::Value& root);

	~ArmorSearch();

	Json::Value getJson();

	ArmorSearch(const ArmorSearch& other); // Copy Constructor
	ArmorSearch(ArmorSearch&& other); // Move Constructor
	ArmorSearch& operator=(const ArmorSearch& other); // Copy Assignment
	ArmorSearch& operator=(ArmorSearch&& other); // Move Assignment


	void searchBySkill(std::vector<Json::Value>& resultList, string& const skillName);
	void searchByName(std::vector<Json::Value>& resultList, string& const armorName);
	//void searchByRank(std::vector<Json::Value>& resultList, string& const rankName);
	//void searchByType(std::vector<Json::Value>& resultList, string& const typeName);
	
private:
	Json::Value* armorJson;
};