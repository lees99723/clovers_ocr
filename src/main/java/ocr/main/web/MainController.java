/*
 * Copyright 2008-2009 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package ocr.main.web;

import java.util.List;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.egovframe.rte.fdl.property.EgovPropertyService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.ui.ModelMap;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.servlet.ModelAndView;
import org.springmodules.validation.commons.DefaultBeanValidator;

import lombok.RequiredArgsConstructor;
import ocr.main.service.MainService;
import ocr.main.service.MainVO;
import ocr.main.service.SearchVO;

/**
 * @Class Name : MainController.java
 * @Description : OCR Main Controller Class
 * @Modification Information
 * @
 * @  수정일      수정자              수정내용
 * @ ---------   ---------   -------------------------------
 * @ 2026.03.30           최초생성
 *
 * @author 이성용
 * @since 2026. 03.30
 * @version 1.0
 * @see
 *
 *  Copyright (C) by MOPAS All right reserved.
 */

@Controller
@RequiredArgsConstructor
public class MainController {

	/** EgovSampleService */
	private final MainService mainService;

	/** EgovPropertyService */
	private final EgovPropertyService propertiesService;

	/** Validator */
	private final DefaultBeanValidator beanValidator;
	
	/**
	 * 메인 페이지
	 * @param searchVO - 조회조건 정보가 담긴 VO
	 * @param model
	 * @return "main"
	 * @exception Exception
	 */
	@RequestMapping("/main.do")
	public String addSampleView(@ModelAttribute("searchVO") SearchVO searchVO, Model model) throws Exception {
		
		model.addAttribute("mainVO", new MainVO());
		return "main";
	}
	
	@RequestMapping(value="/main_list.do", method=RequestMethod.POST)
	public ModelAndView testList(HttpServletRequest request, HttpServletResponse response, ModelMap model) throws Exception {
				
		SearchVO searchVO = new SearchVO();
		
		List<?> mainList = mainService.selectMainList(searchVO);
		model.addAttribute("resultList", mainList);

		ModelAndView mav = new ModelAndView("jsonView");
		mav.addObject("resultList", mainList);
		
		return mav;
	}

}
