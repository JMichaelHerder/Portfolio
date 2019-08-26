// MHW Armor Tool.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <fstream>
#include <typeinfo>

#include "ArmorSearch.h"

using jsonVector = std::vector<Json::Value>;

Json::Value armorJson;

int main()
{
	std::ifstream file("armors.json", std::ifstream::binary);

	file >> armorJson;

	ArmorSearch seeker(armorJson);

	Json::Value val = seeker.getJson();

	jsonVector armorList;

	string skillName = "speed eating6";

	seeker.searchBySkill(armorList, skillName);

	for (Json::Value armor : armorList) {
		std::cout << armor["name_en"] << std::endl;
	}

	seeker.~ArmorSearch();

	return 0;
}
