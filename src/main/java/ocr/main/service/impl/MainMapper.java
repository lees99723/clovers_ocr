/*
 * Copyright 2011 MOPAS(Ministry of Public Administration and Security).
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
package ocr.main.service.impl;

import java.util.List;
import ocr.main.service.MainVO;
import ocr.main.service.SearchVO;

import org.egovframe.rte.psl.dataaccess.mapper.Mapper;

/**
 * ocr main에 관한 데이터처리 매퍼 클래스
 *
 * @author  이성용
 * @since 2026.03.30
 * @version 1.0
 * @see <pre>
 *  == 개정이력(Modification Information) ==
 *
 *          수정일          수정자           수정내용
 *  ----------------    ------------    ---------------------------
 *   2026.03.30        이성용          최초 생성
 *
 * </pre>
 */
@Mapper
public interface MainMapper {

	/**
	 * 목록을 조회한다.
	 * @param mainVO - 조회할 정보가 담긴 VO
	 * @return 목록
	 * @exception Exception
	 */
	List<?> selectMainList(SearchVO searchVO) throws Exception;

}
